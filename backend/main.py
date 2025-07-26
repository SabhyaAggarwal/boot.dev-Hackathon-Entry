from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import uuid
import shutil

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = 'Downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

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

        if not downloaded_file or not os.path.exists(downloaded_file):
            app.logger.error(f"yt-dlp output: {result.stdout}")
            app.logger.error(f"yt-dlp error: {result.stderr}")
            return jsonify({"error": "Failed to determine download file path or file not found."}),500

        filename = os.path.basename(downloaded_file)

        download_link = f"/downloads/{filename}"
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
        return jsonify({"error": "File not found."}), 404

@app.route('/cleanup', methods=['POST'])
def cleanup_downloads():
    try:
        shutil.rmtree(DOWNLOAD_DIR)
        os.makedirs(DOWNLOAD_DIR)
        return jsonify({"message": "Download directory cleaned up."}), 200
    except Exception as e:
        app.logger.error(f"Error during cleanup: {e}")
        return jsonify({"error": f"Failed to clean up: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)


