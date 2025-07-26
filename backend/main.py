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
    return "Video downloader backend is running"

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    if not data or 'video_url' not in data:
        return jsonify({"error": "Missing 'video_url' in request body"}), 400
    video_url = data['video_url']

    unique_filename = str(uuid.uuid4())
    output_path_template = os.path.join(DOWNLOAD_DIR, unique_filename + '.%(ext)s')

    try:
        yt_command = [
            'yt-dlp', '-k',
            '-f', 'bestvideo+bestaudio/best',
            '--merge-output-format', 'mp4',
            '-o', output_path_template, video_url
        ]

        result = subprocess.run(
            yt_command,
            capture_output=True,
            text=True,
            check=True
        )

        downloaded_file =None
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

