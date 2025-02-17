# downloader.py
import yt_dlp

def download_video_function(video_url):
    """
    Функция скачивает видео по ссылке и возвращает название видео.
    """
    try:
        # Настройки для скачивания: сохраняем видео в папку downloads, имя файла будет названием видео с расширением mp4.
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.mp4',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Сначала скачиваем видео
            ydl.download([video_url])
            # Затем получаем информацию о видео (например, название)
            info = ydl.extract_info(video_url, download=False)
            return {"status": "success", "title": info.get("title", "Без названия")}
    except Exception as e:
        return {"status": "error", "error": str(e)}
