import os
import sys
from pathlib import Path
import argparse
from typing import Set, List

class DirectorySelector:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.excluded_paths: Set[Path] = set()
        self.current_path = root_dir

    def get_subdirectories(self, path: Path) -> List[Path]:
        """Get all immediate subdirectories of the given path."""
        try:
            return sorted([p for p in path.iterdir() if p.is_dir() and not p.name.startswith('.')])
        except PermissionError:
            print(f"Permission denied: {path}")
            return []

    def display_menu(self) -> None:
        """Display the current directory and available options."""
        print("\n" + "=" * 60)
        print(f"Current directory: {self.current_path}")
        print("=" * 60)

        # Show parent directory option if not at root
        if self.current_path != self.root_dir:
            print("0: [↑] Go up to parent directory")

        # List all subdirectories
        subdirs = self.get_subdirectories(self.current_path)
        for i, path in enumerate(subdirs, 1):
            status = "[EXCLUDED]" if path in self.excluded_paths else ""
            rel_path = path.relative_to(self.root_dir)
            print(f"{i}: {'  ' * (len(path.parts) - len(self.root_dir.parts))}{path.name} {status}")

        print("\nCommands:")
        print("e: Exclude/Include current directory")
        print("f: Finish selection")
        print("q: Quit without saving")

    def run(self) -> Set[Path]:
        """Run the interactive directory selector."""
        while True:
            self.display_menu()
            choice = input("\nEnter your choice: ").strip().lower()

            if choice == 'q':
                sys.exit(0)
            elif choice == 'f':
                return self.excluded_paths
            elif choice == 'e':
                if self.current_path != self.root_dir:
                    if self.current_path in self.excluded_paths:
                        self.excluded_paths.remove(self.current_path)
                        print(f"\nUnexcluded: {self.current_path}")
                    else:
                        self.excluded_paths.add(self.current_path)
                        print(f"\nExcluded: {self.current_path}")
                else:
                    print("\nCannot exclude root directory!")
            elif choice == '0' and self.current_path != self.root_dir:
                self.current_path = self.current_path.parent
            else:
                try:
                    idx = int(choice) - 1
                    subdirs = self.get_subdirectories(self.current_path)
                    if 0 <= idx < len(subdirs):
                        self.current_path = subdirs[idx]
                    else:
                        print("\nInvalid choice!")
                except ValueError:
                    print("\nInvalid input!")

def add_path_comment(filepath: Path, root_dir: Path) -> None:
    """Add relative path as a comment to the top of the file."""
    rel_path = filepath.relative_to(root_dir)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping binary file: {filepath}")
        return
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return

    extension = filepath.suffix.lower()
    if extension in ['.py', '.sh', '.rb', '.pl']:
        comment = f"# Path: {rel_path}\n"
    elif extension in ['.js', '.java', '.cpp', '.c', '.cs', '.php', '.ts', '.tsx']:
        comment = f"// Path: {rel_path}\n"
    elif extension in ['.html', '.xml']:
        comment = f"<!-- Path: {rel_path} -->\n"
    elif extension in ['.css']:
        comment = f"/* Path: {rel_path} */\n"
    else:
        print(f"Skipping unsupported file type: {filepath}")
        return

    # Check first non-empty line for any kind of path comment
    first_lines = [line.strip() for line in content.split('\n') if line.strip()]
    if first_lines:
        first_line = first_lines[0]
        # Check for path comments in any supported format
        if any(x in first_line.lower() for x in ['path:', 'path :']):
            print(f"Path comment already exists in: {filepath}")
            return

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comment + content)
        print(f"Added path comment to: {filepath}")
    except Exception as e:
        print(f"Error writing to file {filepath}: {e}")

def process_files(directory: Path, excluded_paths: Set[Path]) -> None:
    """Process all files in directory, excluding specified paths."""
    for item in directory.rglob('*'):
        # Skip excluded paths and their children
        if any(str(item).startswith(str(excluded)) for excluded in excluded_paths):
            continue
        if item.is_file():
            add_path_comment(item, directory)

def load_default_excludes() -> set:
    """Load default exclusions from .trailmarkignore file."""
    excludes = set()
    config_files = [
        # Look for config in current directory
        Path('.trailmarkignore'),
        # Look for config in user's home directory
        Path.home() / '.trailmarkignore',
        # Look for config in the same directory as the script
        Path(__file__).parent / '.trailmarkignore'
    ]

    for config_file in config_files:
        if config_file.is_file():
            try:
                with open(config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            excludes.add(line)
            except Exception as e:
                print(f"Warning: Error reading {config_file}: {e}")

    return excludes

# Load default excludes
DEFAULT_EXCLUDES = load_default_excludes()

def main():
    parser = argparse.ArgumentParser(description='Add path comments to files recursively.')
    parser.add_argument('directory', nargs='?', default=os.getcwd(),
                      help='Directory to process (default: current directory)')
    parser.add_argument('-i', '--interactive', action='store_true',
                      help='Run in interactive mode to select directories to exclude')
    parser.add_argument('-a', '--all', action='store_true',
                      help='Process all directories (ignore .trailmarkignore)')
    parser.add_argument('-e', '--exclude', nargs='+', default=[],
                      help='Additional directories to exclude')
    
    args = parser.parse_args()
    root_dir = Path(args.directory)

    if not root_dir.exists() or not root_dir.is_dir():
        print(f"Error: {root_dir} is not a valid directory")
        sys.exit(1)

    excluded_paths = set()

    # Handle different modes
    if args.interactive:
        print("\nWelcome to the interactive directory selector!")
        print("Navigate through directories and mark which ones to exclude.")
        print("Use numbers to navigate, 'e' to exclude/include, 'f' to finish, 'q' to quit.\n")
        
        selector = DirectorySelector(root_dir)
        excluded_paths = selector.run()
    else:
        # Add default exclusions unless -a flag is used
        if not args.all:
            # Find all instances of default excluded directories
            for exclude_dir in DEFAULT_EXCLUDES:
                for path in root_dir.rglob(exclude_dir):
                    if path.is_dir():
                        excluded_paths.add(path)
        
        # Add any additional excluded directories from -e flag
        for exclude_dir in args.exclude:
            for path in root_dir.rglob(exclude_dir):
                if path.is_dir():
                    excluded_paths.add(path)

    # Print summary of what will be excluded
    if excluded_paths:
        print("\nExcluded directories:")
        for path in sorted(excluded_paths):
            print(f"- {path.relative_to(root_dir)}")
    else:
        print("\nNo directories excluded")

    print("\nProcessing files...")
    process_files(root_dir, excluded_paths)
    print("Complete!")

if __name__ == "__main__":
    main()