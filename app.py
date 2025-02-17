import os
import yt_dlp
from flask import Flask, request, jsonify, send_from_directory

# Создаем папку downloads, если она не существует
os.makedirs('downloads', exist_ok=True)

app = Flask(__name__)

def download_video_function(video_url):
    """
    Функция скачивает видео по ссылке и возвращает данные о видео.
    """
    try:
        # Настройки для yt_dlp: сохраняем видео в папку downloads, имя файла = название видео + расширение
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Скачиваем видео
            ydl.download([video_url])
            # Получаем информацию о видео без повторного скачивания
            info = ydl.extract_info(video_url, download=False)
            title = info.get("title", "video")
            ext = info.get("ext", "mp4")
            filename = f"{title}.{ext}"
            return {"status": "success", "title": title, "filename": filename}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.route('/download', methods=['POST'])
def download_endpoint():
    """
    Endpoint для скачивания видео.
    Принимает JSON с ключом "url", скачивает видео и возвращает имя файла.
    """
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Не указана ссылка (url)'}), 400

    video_url = data['url']
    result = download_video_function(video_url)
    if result.get("status") == "error":
        return jsonify(result), 500
    return jsonify(result)

@app.route('/file/<path:filename>', methods=['GET'])
def get_file(filename):
    """
    Endpoint для скачивания файла.
    Возвращает файл из папки downloads.
    """
    return send_from_directory('downloads', filename, as_attachment=True)

if __name__ == '__main__':
    # Запускаем сервер на всех интерфейсах на порту 8080
    app.run(host='0.0.0.0', port=8080)
