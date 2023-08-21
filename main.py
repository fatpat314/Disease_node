import config
from dotenv import load_dotenv
import openai
from flask import Flask, jsonify, request, session, g
from flask_jwt_extended import JWTManager, jwt_required, \
                               create_access_token, get_jwt_identity
import requests, names, random, threading, uuid, json
import argparse

from disease import disease_data, care_provider_disease_data
from gpt import GPT_request, GPT_disease_word_search

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY # change this to a random string in production
CNM_url = "http://localhost:6000"
KAN_url = "http://localhost:8050"
jwt = JWTManager(app)
load_dotenv()

# openai.api_key = config.openai_key

@app.route('/', methods = ['GET'])
def home():
    if(request.method == 'GET'):
        data = "hello Class!"
        return jsonify({'data': data})

@app.route('/disease', methods = ['GET', 'POST'])
@jwt_required()
def disease():
    return disease_data(request, CNM_url, KAN_url)

@app.route('/care_provider_disease', methods = ['GET', 'POST'])
@jwt_required()
def care_provider_disease():
    return care_provider_disease_data(request, CNM_url, KAN_url)

@app.route('/disease_name_search', methods = ['GET', 'POST'])
@jwt_required()
def disease_name_search():
    GPT_result = [f"{request.json.get('text')}"]
    return GPT_disease_word_search(GPT_result)

@app.route('/disease_info', methods = ['GET', 'POST'])
@jwt_required()
def disease_info():
    # print('test')
    disease = request.json.get('item')
    KAN_url_info = f'{KAN_url}/disease_info'
    data = {'disease': disease}
    response = requests.post(KAN_url_info, json=data)
    # print(response.json())
    return jsonify(response.json())

@app.route('/disease_stats', methods = ['GET', 'POST'])
@jwt_required()
def disease_stats():
    disease = request.json.get('item')
    symptoms = request.json.get('message')
    KAN_url_stats = f'{KAN_url}/disease_stats'
    data = {'disease': disease, 'symptoms': symptoms}
    response = requests.post(KAN_url_stats, json=data)
    return jsonify(response.json())


# def GPT_request(age, symptoms):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a Doctor"},
#             {"role": "user", "content": f"The patient is {age} years old and experiencing {str(symptoms)}. What is the diagnosis?"},
#         ]
#     )
#     result = []
#     for choice in response.choices:
#         result.append(choice.message.content)
#     return(result)

# def GPT_disease_word_search(GPT_result):
#     result = "".join(GPT_result)
#     disease_word_search = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a chat bot"},
#             {"role": "user", "content": f"Could you please isolate and return only the disease names in this sentence, separate the diseases by a comma, without any acronyms and say nothing else. If there are no disease names, return 0. '{result}'"},
#         ]
#     )
#     disease_names = ''
#     for choice in disease_word_search.choices:
#         disease_names += choice.message.content
#     if disease_names == 0:
#         return jsonify(result)
    
#     return(disease_names)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8090, help="Port to run the server on")
    args = parser.parse_args()
    port = args.port
    app.run(host="0.0.0.0", port=port)