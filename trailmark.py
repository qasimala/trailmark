# Path: trailmark.py
import os
import sys
import argparse
from pathlib import Path

def add_path_comment(filepath: Path, root_dir: Path) -> None:
    """
    Add relative path as a comment to the top of the file.
    
    Args:
        filepath: Path object of the file to process
        root_dir: Path object of the root directory
    """
    # Get relative path from root directory
    rel_path = filepath.relative_to(root_dir)
    
    # Read the current content of the file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping binary file: {filepath}")
        return
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return

    # Create the comment based on file extension
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

    # Check if the comment already exists
    if content.startswith(comment):
        print(f"Comment already exists in: {filepath}")
        return

    # Write the comment and original content back to the file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comment + content)
        print(f"Added path comment to: {filepath}")
    except Exception as e:
        print(f"Error writing to file {filepath}: {e}")

def should_exclude(path: Path, exclude_patterns: list[str], root_dir: Path) -> bool:
    """
    Check if a path should be excluded based on exclusion patterns.
    
    Args:
        path: Path to check
        exclude_patterns: List of patterns to exclude
        root_dir: Root directory being processed
    
    Returns:
        bool: True if path should be excluded, False otherwise
    """
    # Get relative path from root directory
    try:
        rel_path = path.relative_to(root_dir)
        # Convert to string with forward slashes for consistent matching
        rel_path_str = str(rel_path).replace(os.sep, '/')
        
        for pattern in exclude_patterns:
            # Convert pattern to use forward slashes
            pattern = pattern.replace(os.sep, '/')
            
            # Check if pattern matches at any level
            if pattern in rel_path_str.split('/'):
                return True
                
            # Check if pattern matches the path or any parent
            if rel_path_str == pattern or rel_path_str.startswith(pattern + '/'):
                return True
                
        return False
    except ValueError:
        # If path is not relative to root_dir, don't exclude
        return False
def process_directory(directory: Path, exclude_patterns: list[str]) -> None:
    """
    Recursively process all files in the given directory.
    
    Args:
        directory: Path object of the directory to process
        exclude_patterns: List of path patterns to exclude
    """
    try:
        # Process all files in the directory
        for item in directory.rglob('*'):
            # Skip excluded paths
            if should_exclude(item, exclude_patterns, directory):
                continue
            if item.is_file():
                add_path_comment(item, directory)
    except Exception as e:
        print(f"Error processing directory {directory}: {e}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Add relative path comments to files recursively.')
    parser.add_argument('directory', nargs='?', default=os.getcwd(),
                      help='Directory to process (default: current directory)')
    parser.add_argument('-e', '--exclude', nargs='+', default=[],
                      help='Paths to exclude (e.g., -e node_modules src/temp docs/drafts)')
    
    args = parser.parse_args()
    directory = Path(args.directory)

    # Verify directory exists
    if not directory.exists() or not directory.is_dir():
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)

    print(f"Processing directory: {directory}")
    print(f"Excluding paths: {', '.join(args.exclude) if args.exclude else 'None'}")
    process_directory(directory, args.exclude)
    print("Processing complete!")

if __name__ == "__main__":
    main()