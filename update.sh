#!/bin/bash

set -e
rm -rf updated

remove_padding() {
    local padded_number="$1"
    # Remove leading zeros using parameter expansion
    local unpad_number="${padded_number#"${padded_number%%[!0]*}"}"
    # Handle the case where the number is all zeros
    if [[ -z "$unpad_number" ]]; then
        unpad_number="0"
    fi
    echo "$unpad_number"
}

process_dir() {
  local dir="$1"

  mkdir -p "updated/$dir"

  pattern='([0-9]{2})([0-9]{2}).*\.html'
  for file in `ls ${dir}/*`; do
    if [ -f "$file" ]; then
      echo "Processing $file"
      fname=$(basename $file)

      if [[ $fname =~ $pattern ]]; then
        mo="${BASH_REMATCH[1]}"
        dy="${BASH_REMATCH[2]}"

        month=$(remove_padding $mo)
        day=$(remove_padding $dy)
        echo "matched month=${month} day=${day}"
      fi

      parent_dir="updated/$(dirname $file)"

      out_file="${parent_dir}/${month}-${day}.html"
      echo "out_file=$out_file"
      sed -E 's|http://www\.bibletrack\.org/cgi-bin/bible\.pl\?incr=0&mo=([0-9]+)&dy=([0-9]+)|\1-\2.html|g' "$file" |
      sed -E 's|<img src="\.\./\.\./bible_track_logo.png\"|<img id="logo" src="/bible_track_logo.png"|g' > "$out_file"
    fi
  done
}

process_dir summary/kjv
process_dir summary/nkjv

