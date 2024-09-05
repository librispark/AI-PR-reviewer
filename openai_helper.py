import os
import requests

def get_openai_response(prompt):
    api_key = os.getenv('OPENAI_API_KEY')
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'gpt-4',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.5,
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"OpenAI API returned an error: {response.status_code} - {response.text}")
    
    response_data = response.json()
    
    return response_data
