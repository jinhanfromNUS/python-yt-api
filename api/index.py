from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

# Your CORS policy is correct for the proxy setup.
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

    # Options for yt-dlp: we want the best audio-only stream
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # Don't download, just get the info
        'force_generic_extractor': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # The URL for the best audio stream is usually in the 'url' key
            audio_url = info.get('url')

            if not audio_url:
                raise HTTPException(status_code=404, detail="No suitable audio stream found by yt-dlp.")
            
            return {"audioUrl": audio_url}

    except Exception as e:
        print(f"yt-dlp failed for URL: {url}", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get audio stream using yt-dlp: {str(e)}")