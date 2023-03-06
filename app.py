import os

import openai
from flask import Flask, redirect, render_template, request, url_for
import transutils
from moviepy.editor import *

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

header = {
    'authorization' : os.getenv("ASSEMBLY_KEY"),
    'content_type': 'application/json'
}

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        file = request.files["file"]
        transcribe = getTranscribe(file)
        
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(transcribe),
            temperature=0.6,
            max_tokens=1000
        )
        return redirect(url_for("index", result=response.choices[0].text))
    result = request.args.get("result")
    return render_template("index.html", result=result)
    

def generate_prompt(file):
    return f'${file} please provide feedback in details for an both candidate & interviewer using STAR framework with their ratings '

def getTranscribe(file):
    video = VideoFileClip("D:\\video1083098477.mp4")
    audio = video.audio
    audio.write_audiofile("audio.wav")
    upload_url = transutils.upload_file('audio.wav', header=header)
    
    transcript_res = transutils.request_transcript(upload_url, header)
    polling_endpoint = transutils.make_polling_endpoint(transcript_res)
    transutils.wait_for_completion(polling_endpoint, header)
    paragraphs = transutils.get_paragraphs(polling_endpoint, header)
    res = ""
    for para in paragraphs:
        print(para['text'] + '\n')
        res = res + para['text']
    return res
