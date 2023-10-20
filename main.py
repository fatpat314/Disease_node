import config
from dotenv import load_dotenv
from flask import Flask, jsonify, request, session, g
from flask_jwt_extended import JWTManager, jwt_required, \
                               create_access_token, get_jwt_identity
import requests, names, random, threading, uuid, json
import argparse, ast

from disease import disease_data, care_provider_disease_data, relate_key_symptoms

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
    try:
        data = disease_data(request, CNM_url, KAN_url)
    except:
        return
    return(data)

@app.route('/care_provider_disease', methods = ['GET', 'POST'])
@jwt_required()
def care_provider_disease():
    try:
        disease_data = care_provider_disease_data(request, CNM_url, KAN_url)
    except:
        return
    # get diseases_id
    diseases_id_list = disease_data[1].json()

    # event
    symptoms_id = request.json.get('symptomsData')
    diseases_id = diseases_id_list
    event_url = get_event_server(CNM_url)
    event_url = event_url['url']
    event_url = f'{event_url}/event-symptoms-diseases'
    data = {'symptoms_id': symptoms_id, 'diseases_id': diseases_id}
    event_response = requests.post(event_url, json=data)
    # print("DD", symptoms_id, diseases_id, event_url)

    return jsonify(disease_data[0])

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

@app.route('/key_symptoms', methods = ['GET', 'POST'])
@jwt_required()
def key_symptoms():
    disease = request.json.get('disease_name')
    try:
        KAN_url_key_symptoms = f'{KAN_url}/GPT_key_symptoms'
        data = {'disease': disease}
        response = requests.post(KAN_url_key_symptoms, json=data)
        key_symptoms_list = response.json()
        symptoms_list = ast.literal_eval(key_symptoms_list[0])
        relationship = relate_key_symptoms(symptoms_list, disease, CNM_url)
        relationship = relationship.json()
        # print("RELATIONSHIP", relationship.json())
        symptoms_id = relationship[1]
        diseases_id = relationship[0]
        event_url = get_event_server(CNM_url)
        event_url = event_url['url']
        event_url = f'{event_url}/event-key-symptoms'
        data = {'symptoms_id': symptoms_id, 'diseases_id': diseases_id}
        event_response = requests.post(event_url, json=data)
        print("HELP!!!!")
        return jsonify(symptoms_list)
    except:
        return("ERR")

def get_event_server(cloud_url):
    event_url = f'{cloud_url}/event_server'
    response = requests.get(event_url)
    return response.json()

# def get_diseases_id(disease_name_list, cloud_url):
#     get_id_url = f'{cloud_url}/diseases_id'
#     data = {'diseases': disease_name_list}
#     response = requests.get(get_id_url, json=data)
#     print("DISEASE_ID_LIST", response)
#     return(response)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8090, help="Port to run the server on")
    args = parser.parse_args()
    port = args.port
    app.run(host="0.0.0.0", port=port)