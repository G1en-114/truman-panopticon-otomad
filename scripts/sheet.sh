#!/bin/bash
# usage: sheet.sh video out.jpg [cols rows width] [start] [dur]
v=$1; o=$2; c=${3:-6}; r=${4:-6}; w=${5:-320}; ss=${6:-0}; d=${7:-$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$v")}
n=$((c*r)); fps=$(python3 -I -c "print($n/$d)")
ffmpeg -loglevel error -y -ss $ss -t $d -i "$v" -vf "fps=$fps,scale=$w:-1,tile=${c}x${r}" -frames:v 1 -q:v 4 "$o"
