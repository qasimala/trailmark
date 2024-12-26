# TrailMark

TrailMark is a utility that recursively processes files in a directory and adds their relative paths as comments at the top of each file. This makes it easier to identify file locations when viewing them in isolation, such as in search results or code snippets.

## Features

- Automatically adds path comments to files based on their extension
- Smart comment syntax based on file type
- Skips files that already have path comments
- Interactive directory selection mode
- Configurable directory exclusions via .trailmarkignore
- Available in both Python and Bash implementations

## File Processing

TrailMark processes files in the following way:

1. Checks if the file already has a path comment at the top
   - If a path comment exists (in any supported format), the file is skipped
   - Path comments are identified by the presence of "Path:" (case insensitive)
2. Determines the appropriate comment syntax based on file extension
3. Adds the relative path as a comment at the top of the file
4. Preserves the original file content

## Supported File Types

TrailMark automatically uses the appropriate comment syntax for different file types:

- Python/Shell/Ruby/Perl: `# Path: relative/path/to/file`
- JavaScript/Java/C++/C#/PHP: `// Path: relative/path/to/file`
- HTML/XML: `<!-- Path: relative/path/to/file -->`
- CSS: `/* Path: relative/path/to/file */`

## Configuration

TrailMark uses a `.trailmarkignore` file to specify which directories should be excluded by default. The file can be placed in:

1. The current directory
2. Your home directory (`~/.trailmarkignore`)
3. The same directory as the script

The `.trailmarkignore` file should contain one directory name per line. Lines starting with `#` are treated as comments. Example:

```plaintext
# Package managers
node_modules
venv
vendor

# Version control
.git
.svn

# Build directories
dist
build
target

# Add your own exclusions here
```

If multiple `.trailmarkignore` files exist, they will all be read and their exclusions combined.

## Installation

### Python Version

1. Download `trailmark.py`
2. Make it executable:

```bash
chmod +x trailmark.py
```

### Bash Version

1. Download `trailmark.sh`
2. Make it executable:

```bash
chmod +x trailmark.sh
```

## Usage

Both versions support the same command-line options:

```bash
# Python version
./trailmark.py [options] [directory]

# Bash version
./trailmark.sh [options] [directory]
```

### Command Line Options

- `-i, --interactive`: Run in interactive mode to manually select directories to exclude
- `-a, --all`: Process all directories (ignore .trailmarkignore)
- `-e, --exclude`: Specify additional directories to exclude
  - Python: Space-separated list (`-e dist build temp`)
  - Bash: Comma-separated list (`-e dist,build,temp`)
- `-h, --help`: Show help message

### Default Behavior

By default (no flags), TrailMark will:

- Process the current directory if no directory is specified
- Exclude directories listed in .trailmarkignore
- Process all supported file types
- Skip files that already have path comments
- Add path comments to files that don't have them

### Examples

1. Process current directory using .trailmarkignore:

```bash
./trailmark.py
# or
./trailmark.sh
```

2. Process specific directory:

```bash
./trailmark.py /path/to/project
# or
./trailmark.sh /path/to/project
```

3. Interactive mode:

```bash
./trailmark.py -i
# or
./trailmark.sh -i
```

4. Process all directories (ignore .trailmarkignore):

```bash
./trailmark.py -a
# or
./trailmark.sh -a
```

5. Exclude additional directories:

```bash
# Python (space-separated)
./trailmark.py -e dist build temp

# Bash (comma-separated)
./trailmark.sh -e dist,build,temp
```

6. Combine options:

```bash
# Python
./trailmark.py -i -e dist build /path/to/project

# Bash
./trailmark.sh -i -e dist,build /path/to/project
```

### Interactive Mode

When running with the `-i` flag, TrailMark provides an interactive interface to select directories to exclude:

- Use numbers to navigate into directories
- Use `0` to go up to parent directory
- Use `e` to exclude/include the current directory
- Use `f` to finish selection and start processing
- Use `q` to quit without making changes

## Example Output

Before:

```javascript
function hello() {
  console.log("Hello, world!");
}
```

After:

```javascript
// Path: src/utils/greeting.js
function hello() {
  console.log("Hello, world!");
}
```

## Implementation Differences

While both versions provide the same functionality, there are some implementation differences:

### Python Version

- More portable across operating systems
- Better handling of different text encodings
- More maintainable and easier to extend
- Uses space-separated lists for exclusions

### Bash Version

- Faster execution for large directories
- Better integration with Unix tools
- Uses native file system operations
- Uses comma-separated lists for exclusions

## Tips

- Create a .trailmarkignore file to define your standard exclusions
- Run in interactive mode first to see the directory structure and decide what to exclude
- Use the `-a` flag when you need to process everything, ignoring .trailmarkignore
- Check the script output for any skipped files or errors
- Make sure you have appropriate permissions for all directories you want to process

## Contributing

Feel free to submit issues and enhancement requests!
