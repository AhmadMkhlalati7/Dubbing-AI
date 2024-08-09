import os
import gradio as gr
from create_a_dub_from_url import create_dub_from_url
from create_a_dub_from_file import create_dub_from_file
import shutil

# Ensure the output directory exists
output_directory = "dubbed_videos"
os.makedirs(output_directory, exist_ok=True)

def move_file_to_output_directory(src, dest_directory):
    dest_path = os.path.join(dest_directory, os.path.basename(src))
    if os.path.exists(dest_path):
        os.remove(dest_path)
    shutil.move(src, dest_path)
    return dest_path

def dub_from_url(source_url, source_language, target_language):
    result = create_dub_from_url(source_url, source_language, target_language)
    if result:
        output_path = move_file_to_output_directory(result, output_directory)
        print(output_path)
        return output_path
    else:
        return None

def dub_from_file(input_file, source_language, target_language):
    file_path = input_file.name
    file_format = input_file.type
    result = create_dub_from_file(file_path, file_format, source_language, target_language)
    if result:
        output_path = move_file_to_output_directory(result, output_directory)
        return output_path
    else:
        return None

# Define the list of language options
languages = ["en", "ar", "es", "fr", "de", "it", "pt", "ru", "zh", "ja"]

# Create Gradio interface
url_interface = gr.Interface(
    fn=dub_from_url,
    inputs=[
        gr.Textbox(label="Source URL", lines=1, placeholder="Enter the URL of the video/audio file"),
        gr.Dropdown(label="Source Language", choices=languages, value="en"),
        gr.Dropdown(label="Target Language", choices=languages, value="ar")
    ],
    outputs=gr.Video(label="Dubbed Video/Audio"),
    title="Dub Video or Audio from URL"
)

file_interface = gr.Interface(
    fn=dub_from_file,
    inputs=[
        gr.File(label="Input File"),
        gr.Dropdown(label="Source Language", choices=languages, value="en"),
        gr.Dropdown(label="Target Language", choices=languages, value="ar")
    ],
    outputs=gr.Video(label="Dubbed Video/Audio"),
    title="Dub Video or Audio from File"
)

# Combine both interfaces
app = gr.TabbedInterface(
    interface_list=[url_interface, file_interface],
    tab_names=["Dub from URL", "Dub from File"]
)

if __name__ == "__main__":
    app.launch()
