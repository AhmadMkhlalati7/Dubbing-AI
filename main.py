import gradio as gr
from dubbing_utils import create_dub_from_url

def dub_video(source_url, source_language, target_language):
    result = create_dub_from_url(source_url, source_language, target_language)
    if result:
        return "Dubbing successful! File saved at:", result
    else:
        return "Dubbing failed or timed out."

inputs = [
    gr.Textbox(label="Source URL"),
    gr.Textbox(label="Source Language"),
    gr.Textbox(label="Target Language")
]

outputs = gr.Markdown(label="Output")

iface = gr.Interface(
    fn=dub_video,
    inputs=inputs,
    outputs=outputs,
    title="Video Dubbing"
)

if __name__ == "__main__":
    iface.launch()