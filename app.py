from flask import Flask, redirect, render_template, request, Response, jsonify
from deta import Deta
import uuid
import datetime

from text_processes import transcribe_audio, summarize_text, outline_text

app = Flask(__name__)

# Configure Deta, replace PROJECT KEY with actual API key
dt = Deta("PROJECT KEY")
db = dt.Base("summaries")
drive = dt.Drive("audios")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=['GET'])
def index():
    records_response = db.fetch()
    records = list(records_response.items)
    records.sort(key=lambda x: x['timestamp'], reverse=True)

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

        timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
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

        option = request.form.get('option')

        audio_data = drive.get(audio_file_key)

        processed_data = "bbotob"
        # Call the appropriate function based on the selected option
        # text =  processed_data = transcribe_audio(audio_data)
        # if option == 'transcript':
        #     processed_data = text
        # elif option == 'summary':
        #     processed_data = summarize_text(text)
        # elif option == 'outline':
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

@app.route("/delete/<string:key>", methods=['POST'])
def delete_record(key):
    try:
        db.delete(key)
        return redirect('/')
    except Exception as e:
        print("fail:", e)
        return Response('{"status":"error"}', status=500, mimetype='application/json')


if __name__ == '__main__':
    app.run(port=5000, debug=True)

