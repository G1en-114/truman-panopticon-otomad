#!/bin/bash
# usage: dl.sh outdir BV...
o=$1; shift
for b in "$@"; do
  [ -f "$o/$b.mp4" ] && continue
  .venv/bin/yt-dlp --no-playlist -q --no-warnings --print "%(id)s | %(title)s | %(uploader)s | %(duration)s s | %(view_count)s" --no-simulate -f "bv*[vcodec^=avc1][height<=1080]+ba/b" --merge-output-format mp4 -o "$o/%(id)s.%(ext)s" "https://www.bilibili.com/video/$b/" 2>&1 | tail -2
  sleep 1
done
