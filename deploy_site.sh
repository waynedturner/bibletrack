#!/bin/bash

set -euo pipefail

HOST="ftp.bibletrack.org"
USER_NAME="waynedturner"
PASSWORD="wt-655349OD"
REMOTE_ROOT="/home/waynedturner/public_html"

if [ ! -d "upload/summary2/kjv" ] || [ ! -d "upload/summary2/nkjv" ]; then
  echo "Missing upload/summary2 output. Run ./summary_template.sh first."
  exit 1
fi

if [ ! -d "upload/root" ]; then
  echo "Missing upload/root staging files. Run ./summary_template.sh first."
  exit 1
fi

expect <<EOF
set timeout 900
spawn sftp ${USER_NAME}@${HOST}
expect {
  "yes/no" {
    send "yes\r"
    exp_continue
  }
  "password:" {
    send "${PASSWORD}\r"
  }
}
expect "sftp>"
send "put -r upload/summary2/kjv ${REMOTE_ROOT}/summary2/\r"
expect "sftp>"
send "put -r upload/summary2/nkjv ${REMOTE_ROOT}/summary2/\r"
expect "sftp>"
send "put upload/root/index.html ${REMOTE_ROOT}/index.html\r"
expect "sftp>"
send "put upload/root/Search.html ${REMOTE_ROOT}/Search.html\r"
expect "sftp>"
send "put upload/root/robots.txt ${REMOTE_ROOT}/robots.txt\r"
expect "sftp>"
send "put upload/root/sitemap.xml ${REMOTE_ROOT}/sitemap.xml\r"
expect "sftp>"
send "put upload/root/search-index.json ${REMOTE_ROOT}/search-index.json\r"
expect "sftp>"
send "ls -l ${REMOTE_ROOT}/summary2/kjv/1-1.html\r"
expect "sftp>"
send "ls -l ${REMOTE_ROOT}/summary2/nkjv/1-1.html\r"
expect "sftp>"
send "ls -l ${REMOTE_ROOT}/index.html\r"
expect "sftp>"
send "ls -l ${REMOTE_ROOT}/Search.html\r"
expect "sftp>"
send "ls -l ${REMOTE_ROOT}/robots.txt\r"
expect "sftp>"
send "ls -l ${REMOTE_ROOT}/sitemap.xml\r"
expect "sftp>"
send "ls -l ${REMOTE_ROOT}/search-index.json\r"
expect "sftp>"
send "bye\r"
expect eof
EOF
