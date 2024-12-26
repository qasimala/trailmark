# TrailMark

TrailMark is a utility that recursively processes files in a directory and adds their relative paths as comments at the top of each file. This makes it easier to identify file locations when viewing them in isolation, such as in search results or code snippets.

## Features

- Automatically adds path comments to files based on their extension
- Smart comment syntax based on file type
- Interactive directory selection mode
- Configurable directory exclusions
- Available in both Python and Bash implementations
- Automatically excludes common directories like `node_modules` and `.git`

## Supported File Types

TrailMark automatically uses the appropriate comment syntax for different file types:

- Python/Shell/Ruby/Perl: `# Path: relative/path/to/file`
- JavaScript/Java/C++/C#/PHP: `// Path: relative/path/to/file`
- HTML/XML: `<!-- Path: relative/path/to/file -->`
- CSS: `/* Path: relative/path/to/file */`

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
- `-a, --all`: Process all directories (including those normally excluded by default)
- `-e, --exclude`: Specify additional directories to exclude
  - Python: Space-separated list (`-e dist build temp`)
  - Bash: Comma-separated list (`-e dist,build,temp`)
- `-h, --help`: Show help message

### Default Behavior

By default (no flags), TrailMark will:

- Process the current directory if no directory is specified
- Automatically exclude `node_modules` and `.git` directories
- Process all supported file types
- Add path comments to files that don't already have them

### Examples

1. Process current directory (excluding node_modules and .git):

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

4. Process all directories (including node_modules and .git):

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

- Run in interactive mode first to see the directory structure and decide what to exclude
- Use the `-a` flag when you need to process everything, including normally excluded directories
- Check the script output for any skipped files or errors
- Make sure you have appropriate permissions for all directories you want to process

## Contributing

Feel free to submit issues and enhancement requests!
