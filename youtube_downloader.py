from typing import Any, Dict, Callable

import youtube_dl
from youtube_dl.utils import YoutubeDLError
from multiprocessing.pool import ThreadPool  # Thread pool despite the package

TEST_IDS = ["_eb_1BjvsLQ", "JrsB1RfksEA", "VyNWVdExM24"]

AUDIO_DOWNLOAD_OPTIONS = \
    {'format': "worstaudio/worst",  # For the sake of speed and putting less strain on YT.
     'postprocessors': [{
         'key': 'FFmpegExtractAudio',
         'preferredcodec': 'mp3',
         'preferredquality': '192'}],  # TODO: Reduce?
     'outtmpl': "./%(id)s.%(ext)s",  # https://github.com/ytdl-org/youtube-dl/blob/master/README.md#output-template
     'quiet': "true"  # False for debugging, True for "production"
    }

BASE_URL = "https://www.youtube.com/watch?v="

# TODO: Do we need to notify the caller when a video is done?
# TODO: Limit video length via options to prevent plugging up queue?

class MultiYoutubeDL:
    """Maintains a thread pool that allows for downloading multiple videos at once."""
    def __init__(self, n_threads: int, options: Dict[str, Any]):  # FIXME: Get rid of download_dir
        self._downloader_options = options
        self._thread_pool = ThreadPool(n_threads)

    def submit_job(self, video_id: str, callback: Callable[[str, bool], None]) -> None:
        """Submits an asynchronous download job.
        The supplied callback is called with (video_id, succeeded?) when the job is complete."""
        def job():
            result = False
            try:
                with youtube_dl.YoutubeDL(self._downloader_options) as dl:
                    dl.download([BASE_URL + video_id])
                    result = True
            except YoutubeDLError as e:
                pass  # TODO: Log e
            callback(video_id, result)

        self._thread_pool.apply_async(job)

    def __enter__(self):
        self._thread_pool.__enter__()
        return self

    def __exit__(self, *_):
        self._thread_pool.terminate()
        self._thread_pool.join()
