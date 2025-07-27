# Universal Video Downloader

A simple, web-based tool to download videos from major social media platforms. You can also convert videos to MP3 and clip specific parts of a video — all in one place.

This project was built for the boot.dev hackathon and is hosted on Heroku.

---

## Features

- **Download videos** from:
  - YouTube  
  - Twitter (X)  
  - Reddit  
  - Facebook  
  - And many other platforms supported by `yt-dlp`

- **Convert videos to MP3** (audio only)

- **Clip videos**: choose start and end times to extract just the part you want

- **Supports multiple video formats**

---

## How It Works

- **Frontend**: Simple, easy-to-use interface  
- **Backend**: Flask (Python)  
- **Video Handling**:  
  - `yt-dlp` for downloading  
  - `ffmpeg` for conversion and clipping

Everything runs on a lightweight Flask server deployed to **Heroku**, so no setup is needed on your device.

---

## How to Use

1. **Go to the website**
2. **Paste the video link** from YouTube, Twitter, Reddit, etc.
3. **Select the quality of video** 480p, 720p or 1080p.
4. Or choose:
   - Format: MP4 (video) or MP3 (audio)
   - Start and end time (optional, for clipping)
5. Click **Download**
6. The file will be processed and automatically downloaded

---

## Why This Project?

- One tool for downloading from multiple platforms  
- No ads, no tracking, no unnecessary clutter  
- Useful for students, creators, researchers — anyone who needs to save videos or extract audio

---

## Tech Stack

- **Backend**: Python + Flask  
- **Frontend**: HTML, CSS, Javascript
- **Video Downloader**: [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)  
- **Conversion/Clipping**: [`ffmpeg`](https://ffmpeg.org/)  
- **Hosting**: [Heroku](https://www.heroku.com)

---

## Disclaimer

- This tool is for **educational and personal use only**
- Please respect the **terms of service** of the platforms you download content from
