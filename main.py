import config
from dotenv import load_dotenv
from flask import Flask, jsonify, request, session, g
from flask_jwt_extended import JWTManager, jwt_required, \
                               create_access_token, get_jwt_identity
import requests, names, random, threading, uuid, json
import argparse

from disease import disease_data, care_provider_disease_data

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY # change this to a random string in production
CNM_url = "http://localhost:6000"
KAN_url = "http://localhost:8050"
jwt = JWTManager(app)
load_dotenv()

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

# @app.route('/risk_factors', methods = ['GET', 'POST'])
# @jwt_required()
# def disease_risk_factors():
#     disease = request.json.get('disease_name')
#     # print(disease)
#     KAN_url_risk_factors = f'{KAN_url}/GPT_risk_factors'
#     data = {'disease': disease}
#     response = requests.post(KAN_url_risk_factors, json=data)
#     print(response)
#     return jsonify(response.json())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8090, help="Port to run the server on")
    args = parser.parse_args()
    port = args.port
    app.run(host="0.0.0.0", port=port)