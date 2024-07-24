#!/bin/bash

# Array of month names
months=("January" "February" "March" "April" "May" "June" "July" "August" "September" "October" "November" "December")

# Function to convert month number to month name
month_to_name() {
    local month_num=$1
    # Array indices start at 0, so subtract 1 from month number
    echo "${months[$((month_num - 1))]}"
}

body_file=$(mktemp)
output_file=$(mktemp)

summary_file="$1"
xmllint --html --xpath "//body/*" "$summary_file" | sed 's/&lt;/</g; s/&gt;/>/g; s/&amp;/&/g' > "$body_file"


pattern='([0-9]+)-([0-9]+)\.html'
if [[ $summary_file =~ $pattern ]]; then
  month="${BASH_REMATCH[1]}"
  day="${BASH_REMATCH[2]}"
  echo "matched month=${month} day=${day}"
fi

cat <<EOF > "$output_file"
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BibleTrack Summary: $(month_to_name "$month") ${day}</title>
    <link rel="stylesheet" href="/summary.css">
    <script type="text/javascript" src="/summary_nav.js"></script>
</head>
<body onload="setupNav()">

    <div id="navPane" class="nav-pane">
        <a href="javascript:prev()">Previous</a>
        <a href="javascript:next()">Next</a>
    </div>

EOF

cat "$body_file" >> "$output_file"

cat <<EOF >> "$output_file"
</body>
</html>
EOF

mv "$output_file" "generated.html"