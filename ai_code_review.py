import os
import requests
from github import Github
import json

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

def main():
    # Set up GitHub API client
    github_token = os.getenv('GITHUB_TOKEN')
    g = Github(github_token)
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))

    # Load event data
    with open(os.getenv('GITHUB_EVENT_PATH')) as f:
        event_data = json.load(f)

    # Extract the pull request number
    pr_number = event_data['pull_request']['number']
    
    pr = repo.get_pull(pr_number)

    # Get the changed files
    files = pr.get_files()
    changes = ""
    for file in files:
        if file.status in ['added', 'modified']:
            changes += f"File: {file.filename}\n{file.patch}\n\n"

    # Prepare the prompt
    prompt = f"Review the following code changes for quality and provide feedback:\n{changes}"

    # Get the response from the LLM
    response = get_openai_response(prompt)

    # Check if 'choices' is in the response and handle the error
    if 'choices' in response and len(response['choices']) > 0:
        feedback = response['choices'][0]['message']['content']
        
        # Only post a comment if there's feedback beyond a generic response
        if "looks good" not in feedback.lower() and feedback.strip():
            pr.create_issue_comment(feedback)
        else:
            print("No significant issues found, no comment added.")
    else:
        print("Error: No 'choices' found in the OpenAI API response.")
        print("Full response:", response)

if __name__ == "__main__":
    main()
