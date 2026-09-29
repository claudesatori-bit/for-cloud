#!/bin/bash
# usage: sheet.sh out.jpg  (tiles stills/*.jpg, 3 per row)
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
n=$(ls stills/*.jpg | wc -l); rows=$(( (n+2)/3 ))
$FF -loglevel error -y -pattern_type glob -i 'stills/*.jpg' -vf "scale=640:360,drawtext=text='%{metadata\:none}':fontsize=1,tile=3x${rows}:padding=4" -frames:v 1 "$1" 2>/dev/null || \
$FF -loglevel error -y -pattern_type glob -i 'stills/*.jpg' -vf "scale=640:360,tile=3x${rows}:padding=4" -frames:v 1 "$1"
