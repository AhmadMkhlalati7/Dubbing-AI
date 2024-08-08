import os
import time
import requests
from dotenv import load_dotenv
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


def download_dubbed_file(dubbing_id: str, language_code: str) -> str:
    url = f'https://api.elevenlabs.io/v1/dubbing/{dubbing_id}/audio/{language_code}'
    api_key = os.getenv('ELEVENLABS_API_KEY')
    dir_path = f"data/{dubbing_id}"
    os.makedirs(dir_path, exist_ok=True)

    file_path = f"{dir_path}/{language_code}.mp4"
    if api_key is None:
        raise ValueError('API_KEY environment variable not set')

    headers = {
        'xi-api-key': api_key
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path
    else:
        response.raise_for_status()


def wait_for_dubbing_completion(dubbing_id: str) -> bool:
    """
    Waits for the dubbing process to complete by periodically checking the status.

    Args:
        dubbing_id (str): The dubbing project id.

    Returns:
        bool: True if the dubbing is successful, False otherwise.
    """
    MAX_ATTEMPTS = 120
    CHECK_INTERVAL = 10  # In seconds

    for _ in range(MAX_ATTEMPTS):
        metadata = client.dubbing.get_dubbing_project_metadata(dubbing_id)
        if metadata.status == "dubbed":
            return True
        elif metadata.status == "dubbing":
            print(
                "Dubbing in progress... Will check status again in",
                CHECK_INTERVAL,
                "seconds.",
            )
            time.sleep(CHECK_INTERVAL)
        else:
            print("Dubbing failed:", metadata.error_message)
            return False

    print("Dubbing timed out")
    return False
