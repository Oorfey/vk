import os
import yt_dlp
from flask import Flask, request, jsonify, send_from_directory, abort
import urllib.parse

# Создаем папку для хранения видео, если её нет
os.makedirs('downloads', exist_ok=True)

app = Flask(__name__)

def download_video(video_url):
    """
    Скачивает видео по ссылке video_url и возвращает имя файла (например, "Clip by @novosibka.mp4").
    """
    try:
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Скачиваем видео
            ydl.download([video_url])
            # Получаем информацию о видео (без повторного скачивания)
            info = ydl.extract_info(video_url, download=False)
            title = info.get("title", "video")
            ext = info.get("ext", "mp4")
            filename = f"{title}.{ext}"
            return filename
    except Exception as e:
        print("Ошибка скачивания:", e)
        return None

@app.route('/download', methods=['POST'])
def download_and_return():
    """
    Endpoint принимает POST-запрос на URL:
      https://vk-flask-api.onrender.com/download
    Заголовки должны содержать:
      Orfey: Orfey
    Тело запроса должно быть в формате JSON:
      { "url": "https://vk.com/clip-..." }
      
    После проверки авторизации и наличия ссылки, видео скачивается и сразу возвращается в ответе.
    """
    # Проверка авторизации через заголовок
    auth = request.headers.get('Orfey')
    if auth != 'Orfey':
        return jsonify({"error": "Unauthorized"}), 401

    # Получаем JSON из тела запроса
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Missing 'url' parameter in JSON body"}), 400

    video_url = data['url']
    filename = download_video(video_url)
    if not filename:
        return jsonify({"error": "Error downloading video"}), 500

    # Отдаем файл из папки downloads.
    # Flask корректно работает с именами файлов, даже если они содержат пробелы или специальные символы.
    try:
        return send_from_directory(
            'downloads',
            filename,
            as_attachment=True,
            attachment_filename=filename  # для Flask 2.2+ можно использовать download_name=filename
        )
    except Exception as e:
        print("Ошибка отправки файла:", e)
        return jsonify({"error": "Error sending file"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
