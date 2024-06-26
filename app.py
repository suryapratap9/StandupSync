from flask import Flask, request, jsonify,render_template
from chatGPT import askGPT
from google_calendar_integration import send_calendar_notification
import os
from standup_sync import audioToText
from languages import languages
from standup_analyzer import analyze_weekly_data,askQuestion

app = Flask(__name__)

@app.route('/',methods = ['GET'])
def index():
    return render_template("index.html")

@app.route('/process_audio', methods=['POST'])
def process_audio():
    # Assuming the audio file is sent in the request
    audio_file = request.files['audio']
    language = request.form.get('language')

    if language not in languages.keys():
        return jsonify({
            "Error" : "Error in selected Language "
        })
    
    audio_file.save('output1.wav')  # Save the audio file

    # Perform speech-to-text
    final_text = audioToText(languages[language])

    if final_text == "" or final_text is None:
        response = {
            'status': 'error',
            'message': 'No text to process',
        }
    else:
        # Process the text using GPT
        final_result = askGPT(f"Extract insights, summary, and action items from the transcription of a daily standup meeting (DSM): {final_text}")
        
        # Send the result to Google Calendar
        send_calendar_notification(final_result)

        response = {
            'status': 'success',
            'result': final_result,
            'final_text' : final_text
        }

    # Delete the saved audio file
    os.remove('output1.wav')

    return jsonify(response)

@app.route('/analyse_weekly_data',methods = ['GET'])
def anaylzeWeeklyData():
    return jsonify({
        'results' : analyze_weekly_data()
    })

@app.route('/questions',methods = ['POST'])
def questions():
    question = request.form.get('question')
    response = askQuestion(question)
    return jsonify({
        'result' : response
    })


if __name__ == '__main__':
    app.run(debug=True)