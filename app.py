# app.py
from flask import Flask, request, jsonify
from downloader import download_video_function

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download_endpoint():
    # Получаем JSON-данные из запроса
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Не указана ссылка (параметр url)'}), 400
    
    video_url = data['url']
    # Вызываем функцию скачивания
    result = download_video_function(video_url)
    
    if result.get("status") == "error":
        return jsonify(result), 500
    else:
        return jsonify(result)

if __name__ == '__main__':
    # Запускаем сервер на всех интерфейсах (0.0.0.0) и порту 8080
    app.run(host='0.0.0.0', port=8080)
