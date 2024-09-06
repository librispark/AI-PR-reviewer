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

def get_openai_feedback_with_line_numbers(prompt):
    """Send a formatted patch to OpenAI and return feedback with line numbers."""
    api_key = os.getenv('OPENAI_API_KEY')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    # Define the function schema for returning feedback
    function_schema = {
        "name": "return_feedback_with_line_numbers",
        "description": "Return feedback on each code change with the line number to comment on.",
        "parameters": {
            "type": "object",
            "properties": {
                "feedbacks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "feedback": {
                                "type": "string",
                                "description": "The feedback for the code change."
                            },
                            "lineToAddComment": {
                                "type": "integer",
                                "description": "The line number in the file where the comment should be added."
                            }
                        },
                        "required": ["feedback", "lineToAddComment"]
                    }
                }
            },
            "required": ["feedbacks"]
        }
    }

    # Prepare the prompt to send to the model
    data = {
        'model': 'gpt-4-0613',  # Use model with function calling capability
        'messages': [
            {'role': 'system', 'content': 'You are an AI code reviewer. Your task is to review code changes.'},
            {'role': 'user', 'content': prompt} # f"Please review the following code changes and provide feedback with line numbers:\n{formatted_patch}"
        ],
        'functions': [function_schema],
        'function_call': {'name': 'return_feedback_with_line_numbers'},
        'temperature': 0.5,
    }

    # Make the request to OpenAI
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"OpenAI API returned an error: {response.status_code} - {response.text}")

    response_data = response.json()

    # Check if the function call returned valid data
    if 'choices' in response_data and 'function_call' in response_data['choices'][0]['message']:
        return response_data['choices'][0]['message']['function_call']['arguments']
    else:
        raise Exception("No valid feedback received from OpenAI function call.")
