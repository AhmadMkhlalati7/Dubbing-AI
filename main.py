import os
from typing import Optional
from dotenv import load_dotenv
from dubbing_utils import download_dubbed_file, wait_for_dubbing_completion
from elevenlabs.client import ElevenLabs
import gradio as gr
import requests

# Load environment variables
load_dotenv()

# Retrieve the API key
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError(
        "ELEVENLABS_API_KEY environment variable not found. "
        "Please set the API key in your environment variables."
    )

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def get_video_url(dubbing_id: str, target_language: str) -> Optional[str]:
    try:
        response = requests.get(
            f"https://api.elevenlabs.io/v1/dubbing/{dubbing_id}/audio/{target_language}",
            headers={"xi-api-key": ELEVENLABS_API_KEY}
        )
        response.raise_for_status()
        return response.json().get("url")  # Adjust based on actual response structure
    except Exception as e:
        print(f"Error fetching video URL: {e}")
        return None

def create_dub_from_url(
    source_url: str,
    source_language: str,
    target_language: str,
) -> Optional[str]:
    try:
        response = client.dubbing.dub_a_video_or_an_audio_file(
            source_url=source_url,
            target_lang=target_language,
            mode="automatic",
            source_lang=source_language,
            num_speakers=1,
            watermark=True,
        )
    except Exception as e:
        print(f"Error during dubbing request: {e}")
        return None

    dubbing_id = response.dubbing_id
    print(f"Dubbing ID: {dubbing_id}")

    if wait_for_dubbing_completion(dubbing_id):
        try:
            output_file_path = download_dubbed_file(dubbing_id, target_language)
            video_url = get_video_url(dubbing_id, target_language)
            return video_url if video_url else "Dubbing completed, but video URL not found."
        except Exception as e:
            print(f"Error during file download: {e}")
            return None
    else:
        print("Dubbing did not complete successfully.")
        return None

def dub_video_interface(source_url, source_language, target_language):
    result = create_dub_from_url(source_url, source_language, target_language)
    if result:
        return f"Dubbing was successful! View the video here: {result}"
    else:
        return "Dubbing failed or timed out."

if __name__ == "__main__":
    iface = gr.Interface(
        fn=dub_video_interface,
        inputs=[
            gr.Textbox(label="Source URL"),
            gr.Textbox(label="Source Language"),
            gr.Textbox(label="Target Language")
        ],
        outputs="text",
        title="Dubbing Service",
        description="Enter the URL of the video, the source language, and the target language to create a dubbed version."
    )

    iface.launch(server_name="0.0.0.0", server_port=8081)
