import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from dubbing_utils import download_dubbed_file, wait_for_dubbing_completion
from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not found.")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def create_dub_from_url(source_url, source_language, target_language):
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

    if wait_for_dubbing_completion(dubbing_id):
        try:
            output_file_path = download_dubbed_file(dubbing_id, target_language)
            return output_file_path
        except Exception as e:
            print(f"Error during file download: {e}")
            return None
    else:
        print("Dubbing did not complete successfully.")
        return None

def on_dub_button_click():
    source_url = url_entry.get()
    source_language = source_lang_entry.get()
    target_language = target_lang_entry.get()

    result = create_dub_from_url(source_url, source_language, target_language)
    if result:
        messagebox.showinfo("Success", f"Dubbing was successful! File saved at: {result}")
    else:
        messagebox.showerror("Failure", "Dubbing failed or timed out.")

# Create the main window
root = tk.Tk()
root.title("Dubbing Tool")

# Create and place the widgets
tk.Label(root, text="Source URL:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Source Language:").grid(row=1, column=0, padx=10, pady=10)
source_lang_entry = tk.Entry(root, width=50)
source_lang_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Target Language:").grid(row=2, column=0, padx=10, pady=10)
target_lang_entry = tk.Entry(root, width=50)
target_lang_entry.grid(row=2, column=1, padx=10, pady=10)

dub_button = tk.Button(root, text="Dub Video", command=on_dub_button_click)
dub_button.grid(row=3, column=0, columnspan=2, pady=20)

# Start the GUI event loop
root.mainloop()
