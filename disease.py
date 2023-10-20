from flask import jsonify, request
import requests, json, threading
from flask_jwt_extended import get_jwt_identity

# from gpt import GPT_request, GPT_disease_word_search, GPT_symptoms_disease_correlation

def disease_data(request, CNM_url, KAN_url):
    symptoms_list_data = request.json.get('symptomsData')
    json_list_data = json.dumps(symptoms_list_data)
    patient_id = get_jwt_identity()
    try:
        url = f'{CNM_url}/disease_data'
        data = {'identity': patient_id, 'symptoms': json_list_data}
        response = requests.post(url, json=data)
        current_user_info = response.json()
        age = 2023 - int(current_user_info[0])
        symptoms_list = current_user_info[1]
        # result = GPT_request(age, symptoms_list)# Redundent, move to disease stats for one disease
        KAN_url_gpt = f'{KAN_url}/GPT_request'
        data = {'age': age, 'symptoms_list': symptoms_list}
        result = requests.post(KAN_url_gpt, json=data)
        result = result.json()
        def run_background_task(result):
            KAN_url_disease = f'{KAN_url}/GPT_disease_word_search'
            data = {'result': result}
            disease_names = requests.post(KAN_url_disease, json=data)
            disease_names = disease_names.json()
            disease_list_data = disease_names.split(", ")
            disease_list_json = json.dumps(disease_list_data)
            url = f'{CNM_url}/diseases'
            data = {'diseases': disease_list_json, 'symptoms': json_list_data}
            response = requests.post(url, json=data)
        background_thread = threading.Thread(target=run_background_task, args=(result))
        background_thread.start()
        return(result)
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

def care_provider_disease_data(request, CNM_url, KAN_url):
    symptoms_list_data = request.json.get('symptomsData')
    json_list_data = json.dumps(symptoms_list_data)
    patient_id = request.json.get('patientID')
    try:
        CNM_disease_data_url = f'{CNM_url}/disease_data'
        data = {'identity': patient_id, 'symptoms': json_list_data}
        response = requests.post(CNM_disease_data_url, json=data)
        current_user_info = response.json()
        age = 2023 - int(current_user_info[0])
        symptoms_list = current_user_info[1]

        # result = GPT_request(age, symptoms_list) # Redundent, move to disease stats
        # def run_background_task(result):
        # diseases_names = GPT_disease_word_search(result)

        KAN_url = f'{KAN_url}/disease_data'
        data = {'symptoms': symptoms_list}
        response = requests.post(KAN_url, json=data)

        # disease_names = GPT_symptoms_disease_correlation(symptoms_list) # Move to KAN
        # disease_names = disease_names[1:-1]
        # disease_list_data = disease_names.split('\n')

        disease_data = response.json()
        disease_list_data = disease_data.split(", ")
        disease_list = []
        for i in disease_list_data:
            i = i[1:-1]
            disease_list.append(i)
        disease_list_json = json.dumps(disease_list)
        CNM_disease_url = f'{CNM_url}/diseases'
        data = {'diseases': disease_list_json, 'symptoms': json_list_data}
        res = requests.post(CNM_disease_url, json=data)
        # background_thread = threading.Thread(target=run_background_task, args=(result))
        # background_thread.start()
        return(disease_list, res)
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

def relate_key_symptoms(symptoms, disease, CNM_url):
    try:
        CNM_relate_symptoms_url = f'{CNM_url}/key_symptom_relationships'
        data = {'symptoms': symptoms, 'disease': disease}
        response = requests.post(CNM_relate_symptoms_url, json=data)
        return(response)
    except:
        print("err")
    return("hi")