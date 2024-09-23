from flask import Flask
import logging
import os
import re

import flask
from flask import request
from flask import Response
from flask_cors import CORS, cross_origin

from flask_socketio import SocketIO, emit, join_room

# from goha.ai_engine import generate_response, generate_image
# Use a pipeline as a high-level helper
from transformers import pipeline
from openai import OpenAI
from config import config


# client = OpenAI()
key = config.read_config()
client = OpenAI(api_key=key["API_KEY"])
pipe = pipeline("translation", model="facebook/nllb-200-distilled-600M")

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")  # ,async_mode="gevent_uwsgi"
app.config["socket"] = socketio
CORS(app)
cwd = os.getcwd()

app.config["DOWNLOAD"] = os.path.join(cwd, "download#stats")
try:
    os.mkdir(app.config["DOWNLOAD"])
except:
    pass

logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@app.route("/", methods=["GET", "POST"])
@cross_origin(origin="*")
def altitude():
    header = request.headers.get("Authorization")

    headers_list = request.headers.getlist("X-Forwarded-For")
    e = headers_list  # headers_list[0] if headers_list else request.remote_addr
    ip = str(e).split(",")[0]

    disallowed_characters = "[<>]/*-;+/:()%$#@!/?_\""

    for character in disallowed_characters:
        ip = ip.replace(character, "")

    # header = request.headers["Authorization"]

    msg_received = flask.request.get_json()
    try:
        msg_subject = msg_received["subject"]
    except (KeyError, TypeError):
        return {"Message": "No subject provided to Altitude", "statusCode": 404}
    try:
        if msg_subject == "generate_text":
            return generate_response(msg_received)
        
        elif msg_subject == "generate_image":
            return generate_image(msg_received)
        else:
            return {"Message": "Wrong subject provided to Altitude", "statusCode": 404}
    except Exception as e:
        return {"Message": "Altitude is having trouble understanding your request", "Error": str(e), "statusCode": 500}


def logga(info):
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.critical(info)

def translate_lang(string, src_lang):

    response = pipe(string, src_lang=src_lang, tgt_lang="eng_Latn")
    
    return response




def generate_response(msg_received):
    try:
        string = msg_received["message"]
        src_lang = msg_received["source_lang"]
        tgt_lang = msg_received["target_lang"]
    except KeyError as k:
        return {"Message": "A key for generating text is missing", "Error": str(k), "statusCode": 401}
    
    translated_text = translate_lang(string, src_lang, tgt_lang)
    print(translated_text)

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": translated_text[0]['translation_text']
                }
            ]
        )
        response = completion.choices[0].message
        response = response.content
        # print(completion.choices[0].message)
        # print(type(completion.choices[0].message))
        return {
            "message": "Response success",
            "data": response,
            "statusCode": 200
        }

    except Exception as e:
        return {
            "message": "Error generating text",
            "error": str(e),
            "statusCode": 500
        }
    
def generate_image(msg_received):
    try:
        string = msg_received["message"]
        src_lang = msg_received["source_lang"]
        tgt_lang = msg_received["target_lang"]
    except KeyError as k:
        return {"Message": "A key for generating image is missing", "Error": str(k), "statusCode": 401}

    translated_text = translate_lang(string, src_lang, tgt_lang)

    try:
        response = client.images.generate(
            prompt="A cute baby sea otter",
            n=2,
            size="1024x1024"
        )

        return {
            "message": "Response success",
            "data": response.data[0].url,
            "statusCode": 200
        }
    except Exception as e:
        return {
            "message": "Error generating text",
            "error": str(e),
            "statusCode": 500
        }


# if __name__ == "__main__":
#     # pip install pyopenssl
#     # app.run(host="0.0.0.0", port=5004, debug=True, threaded=True)
#     socketio.run(app, host="0.0.0.0", port=5004, debug=True,
#                  allow_unsafe_werkzeug=True)  # threaded=True, allow_unsafe_werkzeug=True