from flask import Flask, request, render_template_string, jsonify
import os
from dotenv import load_dotenv
from dubbing_utils import download_dubbed_file, wait_for_dubbing_completion
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not found.")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dubbing Tool</title>
</head>
<body>
    <h1>Dubbing Tool</h1>
    <form action="/dub" method="post">
        <label for="source_url">Source URL:</label>
        <input type="text" id="source_url" name="source_url" required><br><br>
        <label for="source_language">Source Language:</label>
        <input type="text" id="source_language" name="source_language" required><br><br>
        <label for="target_language">Target Language:</label>
        <input type="text" id="target_language" name="target_language" required><br><br>
        <input type="submit" value="Dub Video">
    </form>
    {% if result %}
        <h2>Result</h2>
        <p>{{ result }}</p>
    {% endif %}
</body>
</html>
'''

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

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/dub', methods=['POST'])
def dub():
    source_url = request.form['source_url']
    source_language = request.form['source_language']
    target_language = request.form['target_language']

    result = create_dub_from_url(source_url, source_language, target_language)
    if result:
        return render_template_string(HTML_TEMPLATE, result=f"Dubbing was successful! File saved at: {result}")
    else:
        return render_template_string(HTML_TEMPLATE, result="Dubbing failed or timed out.")

if __name__ == "__main__":
    app.run(port=8081)
