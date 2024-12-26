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
    elif extension in ['.js', '.java', '.cpp', '.c', '.cs', '.php']:
        comment = f"// Path: {rel_path}\n"
    elif extension in ['.html', '.xml']:
        comment = f"<!-- Path: {rel_path} -->\n"
    elif extension in ['.css']:
        comment = f"/* Path: {rel_path} */\n"
    else:
        print(f"Skipping unsupported file type: {filepath}")
        return

    if content.startswith(comment):
        print(f"Comment already exists in: {filepath}")
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

def main():
    parser = argparse.ArgumentParser(description='Interactively add path comments to files.')
    parser.add_argument('directory', nargs='?', default=os.getcwd(),
                      help='Directory to process (default: current directory)')
    
    args = parser.parse_args()
    root_dir = Path(args.directory)

    if not root_dir.exists() or not root_dir.is_dir():
        print(f"Error: {root_dir} is not a valid directory")
        sys.exit(1)

    print("\nWelcome to the interactive directory selector!")
    print("Navigate through directories and mark which ones to exclude.")
    print("Use numbers to navigate, 'e' to exclude/include, 'f' to finish, 'q' to quit.\n")

    selector = DirectorySelector(root_dir)
    excluded_paths = selector.run()

    print("\nProcessing files...")
    process_files(root_dir, excluded_paths)
    print("Complete!")

if __name__ == "__main__":
    main()