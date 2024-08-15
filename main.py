import gradio as gr
import os
from typing import Optional
from dotenv import load_dotenv
from dubbing_utils import download_dubbed_file, wait_for_dubbing_completion
from elevenlabs.client import ElevenLabs

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

def create_dub_from_url(
    source_url: str,
    source_language: str,
    target_language: str,
) -> str:
    """
    Downloads a video from a URL, and creates a dubbed version in the target language.

    Args:
        source_url (str): The URL of the source video to dub. Can be a YouTube link, TikTok, X (Twitter) or a Vimeo link.
        source_language (str): The language of the source video.
        target_language (str): The target language to dub into.

    Returns:
        str: The file path of the dubbed file or an error message if the operation failed.
    """
    try:
        response = client.dubbing.dub_a_video_or_an_audio_file(
            source_url=source_url,
            target_lang=target_language,
            mode="automatic",
            source_lang=source_language,
            num_speakers=1,
            watermark=True,  # reduces the characters used
        )
    except Exception as e:
        return f"Error during dubbing request: {e}"

    dubbing_id = response.dubbing_id

    if wait_for_dubbing_completion(dubbing_id):
        try:
            output_file_path = download_dubbed_file(dubbing_id, target_language)
            return f"Dubbing was successful! File saved at: {output_file_path}"
        except Exception as e:
            return f"Error during file download: {e}"
    else:
        return "Dubbing did not complete successfully."

# Gradio Interface
def gradio_interface(source_url, source_language, target_language):
    return create_dub_from_url(source_url, source_language, target_language)

iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Source URL"),
        gr.Textbox(label="Source Language"),
        gr.Textbox(label="Target Language"),
    ],
    outputs="text",
    title="Video Dubbing Interface",
    description="Upload a video URL and get a dubbed version in the target language.",
)

if __name__ == "__main__":
    iface.launch()
