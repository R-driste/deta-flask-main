from flask import Flask, redirect, render_template, request, Response, jsonify
from deta import Deta
import uuid
import datetime

# Import the functions for text summarization and audio transcription (replace with your actual module names)
from text_processes import transcribe_audio, summarize_text, outline_text

# Initialize Flask application
app = Flask(__name__)

# Configure Deta
dt = Deta("b07WpJ6uwom8_KCqJAmGzJkwYLwtM84A1TCDHnKd492jZ")
db = dt.Base("summaries")
drive = dt.Drive("audios")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=['GET', 'POST'])
def index():
    # Retrieve the records using db.fetch() and extract the actual items
    records_response = db.fetch()
    records = list(records_response.items)
    records.sort(key=lambda x: x.timestamp, reverse=True)

    return render_template("index.html", records=records)

@app.route("/create", methods=['POST'])
def create():
    try:
        unique_key = str(uuid.uuid4())[:8]
        audio_file = request.files['audio_file']
        audio_file_key = unique_key + "_" + audio_file.filename[:8]

        if audio_file.content_length > 25 * 1024 * 1024:  # 25 MB limit for Deta Drive
            return Response('{"status":"error", "message":"File size exceeds the limit (25 MB)"}', status=400, mimetype='application/json')

        audio_data = audio_file.stream.read()
        drive.put(data=audio_data, name=f"{audio_file_key}.wav")

        timestamp = datetime.datetime.now().timestamp()
        data = {
            'key': unique_key,
            'name': request.form.get('name'),
            'desc': request.form.get('desc'),
            'option': request.form.get('option'),
            'audio_file_name': audio_file.filename,
            'audio_file_key': audio_file_key,
            'timestamp': timestamp
        }

        db.put(data)

        return redirect('/process')
    except Exception as e:
        print("fail:", e)
        return Response('{"status":"error"}', status=500, mimetype='application/json')

@app.route("/process", methods=['POST'])
def process_request():
    try:
        unique_key = request.form.get('key')
        audio_file_key = request.form.get('audio_file_key')
        option = request.form.get('option')
        print("heeh1")
        # Retrieve the audio file data from Deta Drive
        audio_data = drive.get(audio_file_key)
        print("heeh2")
        processed_data = "bob"
        # Call the appropriate function based on the selected option
        # text =  processed_data = transcribe_audio(audio_data)
        # if option == 'transcript':
        #     processed_data = text
        # elif option == 'summary':
        #     processed_data = summarize_text(text)
        # elif option == 'both':
        #     processed_data = outline_text(text)
        # else:
        #     return Response('{"status":"error", "message":"Invalid option selected"}', status=400, mimetype='application/json')

        # Update the record with the processed data
        record = db.get(unique_key)
        record['processed_data'] = processed_data
        db.put(record, unique_key)

        return redirect('/')
    except Exception as e:
        print("fail:", e)
        return Response('{"status":"error"}', status=500, mimetype='application/json')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
