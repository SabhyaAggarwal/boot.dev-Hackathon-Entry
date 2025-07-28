#!/usr/bin/env bash

set -o errexit

curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
chmod a+rx /usr/local/bin/yt-dlp
echo "yt-dlp installed to /usr/local/bin/yt-dlp"

curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o /tmp/ffmpeg.tar.xz

tar -xf /tmp/ffmpeg.tar.xz -C /tmp/

FFMPEG_DIR=$(find /tmp -maxdepth 1 -type d -name "ffmpeg-*-amd64-static" | head -n 1)

if [ -z "$FFMPEG_DIR" ]; then
    echo "Error: ffmpeg directory not found after extraction. Please check the ffmpeg download URL."
    exit 1
fi

echo "ffmpeg extracted to: $FFMPEG_DIR"

cp "$FFMPEG_DIR"/ffmpeg /usr/local/bin/ffmpeg
cp "$FFMPEG_DIR"/ffprobe /usr/local/bin/ffprobe

chmod a+rx /usr/local/bin/ffmpeg
chmod a+rx /usr/local/bin/ffprobe

pip install -r requirements.txt
