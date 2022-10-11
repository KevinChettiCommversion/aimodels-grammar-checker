from flask import Flask,request , jsonify
import requests
import sys
import json
import pandas as pd
import datetime
from flask_cors import CORS
from happytransformer import HappyTextToText, TTSettings
import spacy
import string

app = Flask(__name__)

CORS(app)
happy_tt = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
args = TTSettings(num_beams=5, min_length=1)
nlp = spacy.load("en_core_web_md")

@app.route('/system-check', methods=["GET"])
def system_check():
    return jsonify({"message": "AI API server is up and running"})

@app.route('/grammar_check', methods=["POST"])
def grammar_check():
    endpoint = "grammar_check"
    req_Json = ""
    try:
        status_code = 200
        if request.method == "POST":
            req_Json = request.json
            text_message = req_Json["text_message"]

            if len(text_message.strip()) == 0:
                outputjson = {"display_message": "Please pass an input", "input": text_message, "output": "",
                              "grammar": None, "error": "",
                              "message": "",
                              "status": 200, "success": True
                              }
                return jsonify(outputjson)

            doc = nlp(text_message)
            grammar = True

            AIGeneratedResponse = ""
            for response_single_message in doc.sents:
                response_single_message = response_single_message.text
                appendedResponse = """grammar: """ + response_single_message
                result = happy_tt.generate_text(appendedResponse, args=args)
                AIGeneratedSingleResponse = result.text
                AIGeneratedResponse = AIGeneratedResponse + AIGeneratedSingleResponse

                print(AIGeneratedSingleResponse)
                display_message = "No grammatical error detected."


                if response_single_message.translate(str.maketrans('', '', string.punctuation)) != AIGeneratedSingleResponse.translate(str.maketrans('', '', string.punctuation)):
                    grammar = False
                    display_message = "Grammar seems to be incorrect."
                    status_code = 201







            outputjson = {"display_message":display_message, "input":text_message, "output":AIGeneratedResponse, "grammar":grammar,  "error": "",
                      "message": "",
                      "status": status_code, "success": True
                      }
            return jsonify(outputjson)



    except Exception as e:
        print(e)
        outputjson = {"display_message": "Some error occurred", "input": text_message, "output": "",
                      "grammar": None, "error": "Some error occurred",
                      "message": "",
                      "status": 202, "success": True
                      }
        return jsonify(outputjson)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=9092)