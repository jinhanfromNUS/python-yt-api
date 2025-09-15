from fastapi import FastAPI, HTTPException
from pytubefix import YouTube
from urllib.parse import unquote

app = FastAPI()

# Add CORS middleware to allow requests from your Next.js app
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",  # Your Next.js development server
#     # Add your production frontend URL here if you deploy
    "https://music-player-frontend-two-beta.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/get_audio_url")
async def get_audio_url(url: str):
    """
    Takes a YouTube URL and returns a direct URL for the best audio stream.
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    try:
        # pytubefix expects a clean URL
        decoded_url = unquote(url)
        yt = YouTube(decoded_url)

        # Filter for audio-only streams, order by bitrate descending, and get the first one
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

        if not audio_stream:
            raise HTTPException(status_code=404, detail="No suitable audio stream found.")

        print(f"pytubefix found audio URL for itag {audio_stream.itag}")
        return {"audioUrl": audio_stream.url}

    except Exception as e:
        print(f"pytubefix failed for URL: {url}", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get audio stream using pytubefix: {str(e)}")