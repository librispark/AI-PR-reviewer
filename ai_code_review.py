import os
import re
import requests
from github import Github
import json
from openai_helper import get_openai_response, get_openai_feedback_with_line_numbers

def post_inline_comment(repo, pr, file, line, comment):
    """Post an inline comment on a specific line of a pull request."""
    print(repo, pr, file, line, comment)
    commit_sha = pr.head.sha
    commit = repo.get_commit(sha=commit_sha)
    pr.create_review_comment(
        body=comment,        # The comment content
        commit=commit,       # The latest commit object
        path=file,           # The file path
        line=line,           # The line number in the file
        side="RIGHT"         # Optional: default to commenting on the "RIGHT" side in split view
    )

def format_patch_with_line_numbers(patch):
    """Format the patch to add line numbers for modified lines."""
    lines = patch.splitlines()
    formatted_patch = []
    current_line_in_new_file = None

    for line in lines:
        # Detect the start of a diff block, e.g., @@ -22,7 +22,7 @@
        match = re.match(r'^@@ \-(\d+),\d+ \+(\d+),\d+ @@', line)
        if match:
            current_line_in_new_file = int(match.group(2))  # Get the starting line number in the new file
            formatted_patch.append(line)  # Add the header line to the formatted patch
            continue

        # If the line starts with a '+' but not '+++' (which is part of the diff header), it's an added line
        if line.startswith('+') and not line.startswith('+++'):
            formatted_patch.append(f"(line: {current_line_in_new_file}) {line}")  # Prepend the line number
            current_line_in_new_file += 1  # Increment the line number for the next added line
        elif not line.startswith('-'):  # If it's not a removed line, increment the line number
            current_line_in_new_file += 1
            formatted_patch.append(line)
        else:
            formatted_patch.append(line)  # Add removed lines as-is for context

    return '\n'.join(formatted_patch)

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

    # Optionally add inline comments on blocks of code, makes multiple API calls, could hit token limits on very code blocks being reviewed
    add_inline_comments = os.getenv('ADD_INLINE_COMMENTS', 'false').lower() == 'true'

    if add_inline_comments:
        for file in files:
            if file.status in ['added', 'modified']:
                # Format the patch to include line numbers
                formatted_patch = format_patch_with_line_numbers(file.patch)

                # Get the feedback from OpenAI
                feedback_response = get_openai_feedback_with_line_numbers(formatted_patch)

                # Parse the feedback into JSON
                feedback_json = json.loads(feedback_response)

                # Post the feedback as inline comments
                for feedback_entry in feedback_json['feedbacks']:
                    feedback = feedback_entry['feedback']
                    line_number = feedback_entry['lineToAddComment']

                    # Post the feedback as an inline comment on the specific line number
                    post_inline_comment(repo, pr, file.filename, line_number, feedback)

    # Add whole PR review comment, makes single API call, more likely to hit input/output token limits depending on PR size
    add_whole_pr_comment = os.getenv('ADD_WHOLE_PR_COMMENT', 'false').lower() == 'true'

    if add_whole_pr_comment:
        # Default behavior: Single API call for all changes
        changes = ""
        for file in files:
            if file.status in ['added', 'modified']:
                changes += f"File: {file.filename}\n{file.patch}\n\n"

        # Prepare the prompt
        prompt = f"Review the following code changes for quality and provide feedback:\n{changes}\n\nIf no issues add #looksgood."

        # Get the response from the LLM
        response = get_openai_response(prompt)

        # Check if 'choices' is in the response and handle the error
        if 'choices' in response and len(response['choices']) > 0:
            feedback = response['choices'][0]['message']['content']
            # Only post a comment if there's feedback beyond a looksgood response
            if "#looksgood" not in feedback.lower() and feedback.strip():
                pr.create_issue_comment(feedback)
            else:
                print("No significant issues found, no comment added.")
        else:
            print("No 'choices' found in the OpenAI API response.")

    if add_whole_pr_comment == 'false' and add_inline_comments == 'false':
        print("Inline and whole PR comments are disabled.")

if __name__ == "__main__":
    main()
