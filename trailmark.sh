#!/bin/bash

# Load default excludes from .trailmarkignore
load_default_excludes() {
    local config_files=(
        ".trailmarkignore"                    # Current directory
        "$HOME/.trailmarkignore"              # Home directory
        "$(dirname "$0")/.trailmarkignore"    # Script directory
    )
    
    local excludes=()
    
    for config_file in "${config_files[@]}"; do
        if [ -f "$config_file" ]; then
            while IFS= read -r line || [ -n "$line" ]; do
                line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                if [ -n "$line" ] && ! [[ "$line" =~ ^# ]]; then
                    excludes+=("$line")
                fi
            done < "$config_file"
        fi
    done
    
    echo "${excludes[@]}"
}

# Default settings
DEFAULT_EXCLUDES=($(load_default_excludes))
INTERACTIVE=false
PROCESS_ALL=false
EXCLUDED_DIRS=()

# Print usage information
usage() {
    echo "Usage: $0 [-i] [-a] [-e dir1,dir2,...] [directory]"
    echo "Options:"
    echo "  -i    Interactive mode"
    echo "  -a    Process all directories (ignore .trailmarkignore)"
    echo "  -e    Additional directories to exclude (comma-separated)"
    echo "  -h    Show this help message"
    exit 1
}

# Function to add comment based on file extension
add_comment() {
    local file="$1"
    local rel_path="$2"
    local ext="${file##*.}"
    local temp_file=$(mktemp)
    
    # Check if file already has a path comment
    if [ -f "$file" ] && grep -qi "path:" "$file" | head -n 1; then
        echo "Path comment already exists in: $file"
        rm "$temp_file"
        return
    fi
    
    # Define comment style based on extension
    case "$ext" in
        py|sh|rb|pl)
            echo "# Path: $rel_path" > "$temp_file"
            ;;
        js|java|cpp|c|cs|php|ts)
            echo "// Path: $rel_path" > "$temp_file"
            ;;
        html|xml)
            echo "<!-- Path: $rel_path -->" > "$temp_file"
            ;;
        css)
            echo "/* Path: $rel_path */" > "$temp_file"
            ;;
        *)
            echo "Skipping unsupported file type: $file"
            rm "$temp_file"
            return
            ;;
    esac
    
    # Append original content
    cat "$file" >> "$temp_file"
    mv "$temp_file" "$file"
    echo "Added path comment to: $file"
}

# Interactive directory selection
interactive_selection() {
    local dir="$1"
    local excluded=()
    
    while true; do
        clear
        echo "Current directory: $dir"
        echo "=================================="
        
        # Show parent directory option if not at root
        if [ "$dir" != "$START_DIR" ]; then
            echo "0: [↑] Go up to parent directory"
        fi
        
        # List subdirectories
        local i=1
        local dirs=()
        while IFS= read -r d; do
            if [ -n "$d" ]; then
                dirs+=("$d")
                local status=""
                if [[ " ${excluded[@]} " =~ " ${d} " ]]; then
                    status="[EXCLUDED]"
                fi
                echo "$i: ${d##*/} $status"
                ((i++))
            fi
        done < <(find "$dir" -maxdepth 1 -mindepth 1 -type d ! -name ".*" | sort)
        
        echo -e "\nCommands:"
        echo "e: Exclude/Include current directory"
        echo "f: Finish selection"
        echo "q: Quit without saving"
        
        read -p $'\nEnter your choice: ' choice
        
        case "$choice" in
            q)
                exit 0
                ;;
            f)
                EXCLUDED_DIRS=("${excluded[@]}")
                return
                ;;
            e)
                if [ "$dir" != "$START_DIR" ]; then
                    if [[ " ${excluded[@]} " =~ " ${dir} " ]]; then
                        excluded=("${excluded[@]/$dir}")
                        echo "Unexcluded: $dir"
                    else
                        excluded+=("$dir")
                        echo "Excluded: $dir"
                    fi
                    read -p "Press Enter to continue..."
                else
                    echo "Cannot exclude root directory!"
                    read -p "Press Enter to continue..."
                fi
                ;;
            0)
                if [ "$dir" != "$START_DIR" ]; then
                    dir="$(dirname "$dir")"
                fi
                ;;
            *)
                if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -gt 0 ] && [ "$choice" -le "${#dirs[@]}" ]; then
                    dir="${dirs[$choice-1]}"
                fi
                ;;
        esac
    done
}

# Parse command line arguments
while getopts ":iae:h" opt; do
    case $opt in
        i)
            INTERACTIVE=true
            ;;
        a)
            PROCESS_ALL=true
            ;;
        e)
            IFS=',' read -ra EXTRA_EXCLUDES <<< "$OPTARG"
            EXCLUDED_DIRS+=("${EXTRA_EXCLUDES[@]}")
            ;;
        h)
            usage
            ;;
        \?)
            echo "Invalid option: -$OPTARG"
            usage
            ;;
    esac
done

# Shift arguments to get the directory
shift $((OPTIND-1))
START_DIR="${1:-.}"

# Verify directory exists
if [ ! -d "$START_DIR" ]; then
    echo "Error: $START_DIR is not a valid directory"
    exit 1
fi

# Convert to absolute path
START_DIR=$(cd "$START_DIR" && pwd)

# Handle interactive mode
if [ "$INTERACTIVE" = true ]; then
    echo "Starting interactive directory selection..."
    interactive_selection "$START_DIR"
fi

# Add default excludes unless -a flag is used
if [ "$PROCESS_ALL" = false ]; then
    EXCLUDED_DIRS+=("${DEFAULT_EXCLUDES[@]}")
fi

# Build find command excludes
FIND_EXCLUDES=""
for dir in "${EXCLUDED_DIRS[@]}"; do
    FIND_EXCLUDES="$FIND_EXCLUDES -not -path '*/$dir/*'"
done

# Show excluded directories
if [ ${#EXCLUDED_DIRS[@]} -gt 0 ]; then
    echo -e "\nExcluded directories:"
    printf -- "- %s\n" "${EXCLUDED_DIRS[@]}"
fi

echo -e "\nProcessing files..."

# Process files
eval "find '$START_DIR' -type f $FIND_EXCLUDES" | while read -r file; do
    rel_path=$(realpath --relative-to="$START_DIR" "$file")
    add_comment "$file" "$rel_path"
done

echo "Complete!"