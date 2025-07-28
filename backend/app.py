from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import uuid
import shutil
import threading
import time
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DOWNLOAD_DIR = 'Downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)
CLEANUP_DELAY_SECONDS = 600

def cleanup_delay(file_path, delay):
    logging.info(f"Scheduling file '{file_path}' for deletion.")
    time.sleep(delay)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Successfully deleted scheduled file: '{file_path}'")
        else:
            logging.warning(f"Attempted to delete file '{file_path}', but it no longer exists.")
    except Exception as e:
        logging.error(f"Error deleting file '{file_path}' : {e}")

@app.route('/')
def index():
    return "Flick-Fetch backend is running"

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    if not data or 'video_url' not in data:
        return jsonify({"error": "Missing 'video_url' in request body"}), 400
    video_url = data['video_url']
    quality = data.get('quality', 'best')

    yt_format = 'bestvideo+bestaudio/best'
    if quality == '480p':
        yt_format = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
    elif quality == '720p':
        yt_format = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
    elif quality == '1080p':
        yt_format = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'

    unique_id = str(uuid.uuid4())
    output_path_template = os.path.join(DOWNLOAD_DIR, unique_id + '.%(ext)s')

    try:
        logging.info(f"Attempting to download video from: {video_url} with quality: {quality}")
        yt_command = [
            'yt-dlp', '-k',
            '-f', yt_format,
            '--merge-output-format', 'mp4',
            '-o', output_path_template, video_url
        ]

        result = subprocess.run(
            yt_command,
            capture_output=True,
            text=True,
            check=True
        )

        downloaded_file = None
        for line in result.stdout.splitlines():
            if 'Destination: ' in line:
                downloaded_file = line.split('Destination:')[1].strip()
                break
            elif '[Merger] Merging formats into' in line:
                downloaded_file = line.split('[Merger] Merging formats into')[1].strip().replace('"', '')
                break

        if downloaded_file:
            filename_from_ytdlp = os.path.basename(downloaded_file)
            full_download_path = os.path.join(DOWNLOAD_DIR, filename_from_ytdlp)

            if not os.path.exists(full_download_path):
                app.logger.error(f"yt-dlp reported '{downloaded_file}', but file not found at '{full_download_path}'")
                app.logger.error(f"yt-dlp stdout: {result.stdout}")
                app.logger.error(f"yt-dlp stderr: {result.stderr}")
                return jsonify({"error": "Failed to determine download file path or file not found."}),500

            downloaded_file = full_download_path

        if not downloaded_file or not os.path.exists(downloaded_file):
            app.logger.error(f"yt-dlp output: {result.stdout}")
            app.logger.error(f"yt-dlp error: {result.stderr}")
            return jsonify({"error": "Failed to determine download file path or file not found."}),500

        filename = os.path.basename(downloaded_file)

        cleanup_thread = threading.Thread(
            target = cleanup_delay,
            args = (downloaded_file, CLEANUP_DELAY_SECONDS) 
        )
        cleanup_thread.daemon = True
        cleanup_thread.start()

        download_link = f"/downloads/{filename}"
        logging.info(f"Video '{filename}' downloaded successfully. Link {download_link}")
        return jsonify({
            "message": "Video downloaded successfully",
            "filename": filename,
            "download_link": download_link
        }), 200

    except subprocess.CalledProcessError as e:
        app.logger.error(f"yt-dlp command failed: {e}")
        app.logger.error(f"stdout: {e.stdout}")
        app.logger.error(f"stderr: {e.stderr}")
        return jsonify({"error": f"Video download failed: {e.stderr.strip()}"}), 500
    except FileNotFoundError:
        return jsonify({"error": "yt-dlp not found."}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/convert_mp4_to_mp3', methods=['POST'])
def convert_mp4_to_mp3():

    data = request.get_json()
    if not data or 'video_url' not in data:
        return jsonify({"error": "Missing 'video_url' in request body"}), 400
    
    video_url = data['video_url']

    unique_video_id = str(uuid.uuid4())
    video_output_path_template = os.path.join(DOWNLOAD_DIR, unique_video_id + '.%(ext)s')
    try:
        logging.info(f"Attempting to download video for MP3 conversion from: {video_url}")
        yt_command = [
            'yt-dlp', '-k',
            '-f', bestaudio/best,
            '-x',
            '--audio-format', 'mp3',
            '-o', video_output_path_template, video_url
        ]

        result = subprocess.run(
            yt_command,
            capture_output=True,
            text=True,
            check=True
        )

        downloaded_audio_file = None
        for line in result.stdout.splitlines():
            if '[ExtractAudio] Destination:' in line:
                downloaded_audio_file = line.split('to "')[1].split('"')[0].strip()
                break
            elif '[ExtractAudio] Convertung audio' in line:
                downloaded_audio_file = line,split('to "')[1].split('"')[0].strip()
                break


        if downloaded_audio_file:
            filename_from_ytdlp = os.path.basename(downloaded_audio_file)
            full_download_path = os.path.join(DOWNLOAD_DIR, filename_from_ytdlp)

            if not os.path.exists(full_downloaded_path):
                app.logger.error(f"yt-dlp reported '{downloaded_audio_file}', but file not found at '{full_downloaded_path}'")
                app.logger.error(f"yt-dlp stdout: {result.stdout}")
                app.logger.error(f"yt-dlp stderr: {result.stderr}")
                return jsonify({"error": "Failed to determine downloaded audio file path or file not found after conversion."}), 500
            
            downloaded_audio_file = full_downloaded_path

        if not downloaded_audio_file or not os.path.exists(downloaded_audio_file):
            app.logger.error(f"yt-dlp output: {result.stdout}")
            app.logger.error(f"yt-dlp error: {result.stderr}")
            return jsonify({"error": "Failed to determine converted audio file path or file not found."}), 500

        filename = os.path.basename(downloaded_audio_file)
        
        cleanup_thread = threading.Thread(
            target=cleanup_file_after_delay,
            args=(downloaded_audio_file, CLEANUP_DELAY_SECONDS)
        )
        cleanup_thread.daemon = True
        cleanup_thread.start()

        download_link = f"/downloads/{filename}"
        logging.info(f"Audio '{filename}' converted successfully. Link: {download_link}")
        return jsonify({
            "message": "Video converted to MP3 successfully",
            "filename": filename,
            "download_link": download_link
        }), 200

    except subprocess.CalledProcessError as e:
        app.logger.error(f"Conversion command failed: {e}")
        app.logger.error(f"stdout: {e.stdout}")
        app.logger.error(f"stderr: {e.stderr}")
        return jsonify({"error": f"MP4 to MP3 conversion failed: {e.stderr.strip()}"}), 500
    except FileNotFoundError:
        app.logger.error("ffmpeg or yt-dlp not found. Ensure they are installed and in your system's PATH.")
        return jsonify({"error": "ffmpeg or yt-dlp not found. Please ensure they are installed and in your system's PATH."}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during conversion: {e}")
        return jsonify({"error": f"An unexpected error occurred during conversion: {str(e)}"}), 500


@app.route('/clip_video', methods=['POST'])
def clip_video():
    data = request.get_json()
    if not data or 'video_url' not in data or 'start_time' not in data or 'end_time' not in data:
        return jsonify({"error": "Missing 'video_url', 'start_time', or 'end_time' in request body"}), 400

    video_url = data['video_url']
    start_time = data['start_time']
    end_time = data['end_time']

    unique_id = str(uuid.uuid4())
    downloaded_video_path = os.path.join(DOWNLOAD_DIR, unique_download_id + '.mp4') # Force mp4 for clipping

    try:
        logging.info(f"Attempting to download video for clipping from: {video_url}")
        yt_dlp_command = [
            'yt-dlp',
            '-f', 'bestvideo+bestaudio/best',
            '--merge-output-format', 'mp4',
            '-o', downloaded_video_path,
            video_url
        ]
        
        subprocess.run(
            yt_dlp_command,
            capture_output=True,
            text=True,
            check=True
        )

        if not os.path.exists(downloaded_video_path):
            app.logger.error(f"Downloaded video for clipping not found at: {downloaded_video_path}")
            return jsonify({"error": "Failed to download video for clipping."}), 500

        unique_clip_id = str(uuid.uuid4())
        clipped_video_filename = f"clipped_{unique_clip_id}.mp4"
        clipped_video_path = os.path.join(DOWNLOAD_DIR, clipped_video_filename)

        logging.info(f"Clipping video '{downloaded_video_path}' from {start_time} to {end_time}")
        ffmpeg_command = [
            'ffmpeg',
            '-i', downloaded_video_path, 
            '-ss', start_time,
            '-to', end_time,
            '-c', 'copy',
            clipped_video_path 
        ]

        subprocess.run(
            ffmpeg_command,
            capture_output=True,
            text=True,
            check=True
        )

        if not os.path.exists(clipped_video_path):
            app.logger.error(f"Clipped video not found at: {clipped_video_path}")
            return jsonify({"error": "Failed to create clipped video."}), 500

        cleanup_thread_original = threading.Thread(
            target=cleanup_file_afterdelay,
            args=(downloaded_video_path, CLEANUP_DELAY_SECONDS)
        )
        cleanup_thread_original.daemon = True
        cleanup_thread_original.start()

        cleanup_thread_clipped = threading.Thread(
            target=cleanup_file_afterdelay,
            args=(clipped_video_path, CLEANUP_DELAY_SECONDS)
        )
        cleanup_thread_clipped.daemon = True
        cleanup_thread_clipped.start()

        download_link = f"/downloads/{clipped_video_filename}"
        logging.info(f"Video clipped successfully. Link: {download_link}")
        return jsonify({
            "message": "Video clipped successfully",
            "filename": clipped_video_filename,
            "download_link": download_link
        }), 200

    except subprocess.CalledProcessError as e:
        app.logger.error(f"Clipping command failed: {e}")
        app.logger.error(f"stdout: {e.stdout}")
        app.logger.error(f"stderr: {e.stderr}")
        return jsonify({"error": f"Video clipping failed: {e.stderr.strip()}"}), 500
    except FileNotFoundError:
        app.logger.error("ffmpeg or yt-dlp not found. Ensure they are installed and in your system's PATH.")
        return jsonify({"error": "ffmpeg or yt-dlp not found. Please ensure they are installed and in your system's PATH."}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during clipping: {e}")
        return jsonify({"error": f"An unexpected error occurred during clipping: {str(e)}"}), 500

@app.route('/downloads/<filename>')
def serve_downloaded_file(filename):
    try:
        return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        logging.warning(f"Requested file '{filename}' not found in '{DOWNLOAD_DIR}'.")
        return jsonify({"error": "File not found."}), 404

@app.route('/cleanup', methods=['POST'])
def cleanup_downloads():
    try:
        if os.path.exists(DOWNLOAD_DIR):
            shutil.rmtree(DOWNLOAD_DIR)
            logging.info(f"Removed existing '{DOWNLOAD_DIR}' directory.")
        os.makedirs(DOWNLOAD_DIR)
        logging.info(f"Recreated empty '{DOWNLOAD_DIR}' directory.")
        return jsonify({"message": "Download directory cleaned up."}), 200
    except Exception as e:
        app.logger.error(f"Error during cleanup: {e}")
        return jsonify({"error": f"Failed to clean up: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

