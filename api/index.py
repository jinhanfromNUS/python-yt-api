from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

# This CORS policy is correct for your proxy setup.
origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/get_audio_url")
async def get_audio_url(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    # This is the new, crucial configuration for yt-dlp.
    # We are forcing it to act like the YouTube Music client for Android.
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android_music']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract information about the video
            info = ydl.extract_info(url, download=False)
            
            # Find the best audio stream from the list of available formats
            best_audio_format = None
            if 'formats' in info:
                for f in info['formats']:
                    # We are looking for an audio-only stream ('vcodec': 'none')
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        # Pick the one with the highest average bitrate (abr)
                        if best_audio_format is None or (f.get('abr', 0) > best_audio_format.get('abr', 0)):
                            best_audio_format = f

            # If we couldn't find a suitable format, raise an error
            if not best_audio_format or not best_audio_format.get('url'):
                raise HTTPException(status_code=404, detail="No suitable audio-only stream found by yt-dlp.")
            
            return {"audioUrl": best_audio_format['url']}

    except Exception as e:
        print(f"yt-dlp failed for URL: {url}", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get audio stream using yt-dlp: {str(e)}")