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
    dir_path = f"data/{dubbing_id}"
    os.makedirs(dir_path, exist_ok=True)

    file_path = f"{dir_path}/{language_code}.mp4"

    headers = {
        'xi-api-key': ELEVENLABS_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        if response.content:  # Ensure content is not empty
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return file_path
        else:
            raise ValueError("No content received from the API")
    
    except requests.exceptions.RequestException as e:
        print(f"Request error occurred: {e}")
        raise
    except ValueError as e:
        print(f"Value error occurred: {e}")
        raise


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
        try:
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
        
        except Exception as e:
            print(f"Error checking dubbing status: {e}")
            return False

    print("Dubbing timed out")
    return False
