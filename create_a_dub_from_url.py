from flask import Flask, render_template, request
from dubbing_utils import create_dub_from_url

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dub', methods=['POST'])
def dub_video():
    source_url = request.form.get('source_url')
    source_language = request.form.get('source_language')
    target_language = request.form.get('target_language')

    result = create_dub_from_url(source_url, source_language, target_language)

    if result:
        # Display success message or provide a download link in the template
        return render_template('success.html', output_file_path=result)
    else:
        # Display error message in the template
        return render_template('error.html')
    

if __name__ == '__main__':
    app.run(debug=True)    
