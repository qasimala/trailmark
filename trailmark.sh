# Path: trailmark.sh
#!/bin/bash

# Function to add comment based on file extension
add_comment() {
    local file="$1"
    local rel_path="$2"
    local ext="${file##*.}"
    
    case "$ext" in
        py|sh|rb|pl)
            sed -i "1i# Path: $rel_path" "$file"
            ;;
        js|java|cpp|c|cs|php)
            sed -i "1i// Path: $rel_path" "$file"
            ;;
        html|xml)
            sed -i "1i<!-- Path: $rel_path -->" "$file"
            ;;
        css)
            sed -i "1i/* Path: $rel_path */" "$file"
            ;;
    esac
}

# Main script
dir="${1:-.}"
exclude_pattern="${2:-}"

# Use find with exclusion patterns
find "$dir" -type f ! -path "*/\.*" ${exclude_pattern:+-not -path "$exclude_pattern"} | while read -r file; do
    rel_path=$(realpath --relative-to="$dir" "$file")
    add_comment "$file" "$rel_path"
done