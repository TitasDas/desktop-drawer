#!/usr/bin/env bash
# Soundtrack with a soft whoosh at each caption change, MP4, poster and GIF teaser.
set -euo pipefail
cd "$(dirname "$0")"
MUSIC="${1:-wallpaper.mp3}"; SKIP="${2:-6}"
DUR=$(python3 -c "import json; print(json.load(open('timing.json'))['duration'])")
STARTS=$(python3 -c "import json; print(' '.join('%.3f'%s for s in json.load(open('timing.json'))['cue_starts']))")
ffmpeg -v error -y -f lavfi -i "anoisesrc=color=pink:amplitude=0.5:duration=0.6:sample_rate=44100" -af "bandpass=f=700:width_type=o:w=1.4,afade=t=in:st=0:d=0.2,afade=t=out:st=0.25:d=0.35,volume=0.8" whoosh.wav
N=$(echo $STARTS | wc -w)
INPUTS="-i $MUSIC"; FILTER="[0:a]atrim=start=$SKIP,asetpts=PTS-STARTPTS,volume=0.30,afade=t=in:st=0:d=1.5,afade=t=out:st=$(python3 -c "print($DUR-2.5)"):d=2.5[m];"; MIX="[m]"; k=1
for s in $STARTS; do INPUTS="$INPUTS -i whoosh.wav"; ms=$(python3 -c "print(int($s*1000))"); FILTER="$FILTER[$k:a]adelay=${ms}|${ms},volume=0.22[w$k];"; MIX="$MIX[w$k]"; k=$((k+1)); done
FILTER="$FILTER${MIX}amix=inputs=$((N+1)):normalize=0:duration=first[aout]"
ffmpeg -v error -y $INPUTS -filter_complex "$FILTER" -map "[aout]" -t "$DUR" -ar 44100 -ac 2 audio.wav
ffmpeg -v error -y -framerate 25 -i frames/%05d.png -i audio.wav -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 160k -shortest usage-demo.mp4
ffmpeg -v error -y -ss 3.2 -i usage-demo.mp4 -frames:v 1 -q:v 3 usage-demo-poster.jpg
ffmpeg -v error -y -framerate 25 -start_number 0 -i frames/%05d.png -frames:v 190 -vf "fps=10,scale=560:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" teaser.gif
ls -la usage-demo.mp4 usage-demo-poster.jpg teaser.gif
