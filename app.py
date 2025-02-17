import os
import yt_dlp
from flask import Flask, request, jsonify, send_from_directory
import urllib.parse

# Создаем папку для хранения видео, если её нет
os.makedirs('downloads', exist_ok=True)

app = Flask(__name__)

def download_video(video_url):
    """
    Скачивает видео по ссылке video_url с наилучшим качеством, пытаясь избежать перекодировки,
    и возвращает имя файла.
    """
    try:
        ydl_opts = {
            # Выбираем наилучшие видео и аудио потоки в формате mp4 и m4a
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'merge_output_format': 'mp4',  # объединяем в mp4
            # Передаем аргументы для ffmpeg, чтобы попробовать выполнить копирование потоков без перекодировки
            'postprocessor_args': ['-c', 'copy']
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
    Принимает POST-запрос с заголовком авторизации и JSON-телом:
      Headers: Orfey: Orfey
      Body (JSON): { "url": "https://vk.com/clip-..." }
    Скачивает видео и сразу возвращает файл в ответе.
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

    try:
        return send_from_directory(
            'downloads',
            filename,
            as_attachment=True,
            download_name=filename  # Flask 2.2+ параметр для имени файла
        )
    except Exception as e:
        print("Ошибка отправки файла:", e)
        return jsonify({"error": "Error sending file"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
