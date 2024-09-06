import os
import requests
from github import Github
import json
from openai_helper import get_openai_response

def main():
    # Set up GitHub API client
    github_token = os.getenv('GITHUB_TOKEN')
    g = Github(github_token)
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))

    # Load event data
    with open(os.getenv('GITHUB_EVENT_PATH')) as f:
        event_data = json.load(f)

    # Extract the issue or pull request number from the event data
    issue_number = event_data['issue']['number']

    print(f"issue_number: {issue_number}")

    issue = repo.get_issue(int(issue_number))

    # Fetch the latest comment that triggered the workflow
    latest_comment = event_data['comment']['body']

    # Fetch the previous comments for context
    comments = issue.get_comments()
    comment_history = "\n".join([comment.body for comment in comments])

    # Prepare the prompt
    prompt = f"""
    You are an AI assistant. Below is a conversation about a pull request. Please respond to the latest comment intelligently.

    Comment history:
    {comment_history}

    Latest comment:
    {latest_comment}
    """

    # Get the response from the AI
    response = get_openai_response(prompt)

    # Check if 'choices' is in the response and handle the error
    if 'choices' in response and len(response['choices']) > 0:
        feedback = response['choices'][0]['message']['content']

        # Post the AI's response as a comment
        issue.create_comment(feedback)
    else:
        print("Error: No 'choices' found in the OpenAI API response.")
        print("Full response:", response)

if __name__ == "__main__":
    main()
