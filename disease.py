from flask import jsonify, request
import requests, json, threading
from flask_jwt_extended import get_jwt_identity

from gpt import GPT_request, GPT_disease_word_search, GPT_symptoms_disease_correlation

def disease_data(request, cloud_url):
    symptoms_list_data = request.json.get('symptomsData')
    json_list_data = json.dumps(symptoms_list_data)
    patient_id = get_jwt_identity()
    try:
        url = f'{cloud_url}/disease_data'
        data = {'identity': patient_id, 'symptoms': json_list_data}
        response = requests.post(url, json=data)
        current_user_info = response.json()
        age = 2023 - int(current_user_info[0])
        symptoms_list = current_user_info[1]
        result = GPT_request(age, symptoms_list)
        def run_background_task(result):
            disease_names = GPT_disease_word_search(result)
            disease_list_data = disease_names.split(", ")
            disease_list_json = json.dumps(disease_list_data)
            url = f'{cloud_url}/diseases'
            data = {'diseases': disease_list_json, 'symptoms': json_list_data}
            response = requests.post(url, json=data)
        background_thread = threading.Thread(target=run_background_task, args=(result))
        background_thread.start()
        print(result)
        return jsonify(result)
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

def care_provider_disease_data(request, cloud_url):
    symptoms_list_data = request.json.get('symptomsData')
    json_list_data = json.dumps(symptoms_list_data)
    patient_id = request.json.get('inputValue')
    try:
        url = f'{cloud_url}/disease_data'
        data = {'identity': patient_id, 'symptoms': json_list_data}
        response = requests.post(url, json=data)
        current_user_info = response.json()
        age = 2023 - int(current_user_info[0])
        symptoms_list = current_user_info[1]
        result = GPT_request(age, symptoms_list)
        # def run_background_task(result):
        # disease_names = GPT_disease_word_search(result)
        disease_names = GPT_symptoms_disease_correlation(symptoms_list)
        disease_names = disease_names[1:-1]
        # disease_list_data = disease_names.split('\n')
        disease_list_data = disease_names.split(", ")
        disease_list = []
        for i in disease_list_data:
            i = i[1:-1]
            disease_list.append(i)
        disease_list_json = json.dumps(disease_list)
        url = f'{cloud_url}/diseases'
        data = {'diseases': disease_list_json, 'symptoms': json_list_data}
        res = requests.post(url, json=data)
        # background_thread = threading.Thread(target=run_background_task, args=(result))
        # background_thread.start()
        print(result, disease_list)
        return jsonify(result, disease_list)
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400