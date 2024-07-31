#!/bin/bash

set -e
# Array of month names
months=("January" "February" "March" "April" "May" "June" "July" "August" "September" "October" "November" "December")

# Function to convert month number to month name
month_to_name() {
    local month_num=$1
    # Array indices start at 0, so subtract 1 from month number
    echo "${months[$((month_num - 1))]}"
}

function extract_lines {
    local file=$1
    local start_pattern=$2
    local end_pattern=$3
    local out_file=$4

    local start_line=1

    if [ -z "$start_pattern" ]; then
      start_line=1
    else
      # Find the line numbers
      start_line=$(grep -n -i "$start_pattern" "$file" | cut -d: -f1)
      start_line=$((start_line+1))
    fi

    local end_line
    end_line=$(grep -n -i "$end_pattern" "$file" | cut -d: -f1)
    end_line=$((end_line-1))

    if [ -z "$out_file" ]; then
      sed -n "${start_line},${end_line}p" "$file"
    else
      sed -n "${start_line},${end_line}p" "$file" > "$out_file"
    fi

}

next_uri() {
  # Start date
  local month=$1
  local day=$2
  # Convert to seconds since epoch
  start_seconds=$(date -j -f "%m-%d" "${month}-${day}" "+%s")

  # Increment by one day (86400 seconds)
  next_seconds=$((start_seconds + 86400))

  # Convert back to date format
  date -j -f "%s" "$next_seconds" "+%-m-%-d.html"
}

prev_uri() {
  # Start date
  local month=$1
  local day=$2
  # Convert to seconds since epoch
  start_seconds=$(date -j -f "%m-%d" "${month}-${day}" "+%s")

  # decrement by one day (86400 seconds)
  prev_seconds=$((start_seconds - 86400))

  # Convert back to date format
  date -j -f "%s" "$prev_seconds" "+%-m-%-d.html"
}

generate_summary() {
  local summary_file=$1
  local out_file=$2

  local body_file="${out_file}.tmp"
  local summary_tmp="/tmp/summary.tmp"

  extract_lines "$summary_file" "<body*" "</body>" > "$body_file"

  pattern='([0-9]+)-([0-9]+)\.html'
  if [[ $summary_file =~ $pattern ]]; then
    month="${BASH_REMATCH[1]}"
    day="${BASH_REMATCH[2]}"

  fi

  next_url=$(next_uri "$month" "$day")
  prev_url=$(prev_uri "$month" "$day")

  if [ ! -e "$summary_tmp" ]; then
    extract_lines "summary_template.html" "" "{{body}}" > "$summary_tmp"
  fi

  sed "s/{{month}}/$(month_to_name "$month")/g" "$summary_tmp" |
  sed "s/{{day}}/$day/g" |
  sed "s/{{next_url}}/$next_url/g" |
  sed "s/{{prev_url}}/$prev_url/g" > "$out_file"


  cat "$body_file" >> "$out_file"
  rm -rf "$body_file"

  echo "</body></html>" >> "$out_file"

}

all="$1"

rm -rf upload

if [ -z "$all" ]; then
  changed_files=$(git diff --name-only HEAD~1 HEAD | grep ^summary/)
else
  changed_files=$(find ./summary2 -iname "*.html")
fi

for changed_file in $changed_files; do
  dir=$(dirname "$changed_file")
  name=$(basename "$changed_file")
  output_dir="./upload/$dir"
  mkdir -p "$output_dir"
  echo "generate summary $changed_file"
  generate_summary "$changed_file" "$output_dir/$name"
done


