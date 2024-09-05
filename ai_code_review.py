import os
import requests
from github import Github
import json
from openai_helper import get_openai_response

def post_inline_comment(repo, pr, file, line, comment):
    pr.create_review_comment(body=comment, commit_id=pr.head.sha, path=file, position=line)

def group_code_blocks(patch, context_lines=0):
    """Groups consecutive added/modified lines into blocks and includes context lines above and below."""
    lines = patch.splitlines()
    code_blocks = []
    current_block = []
    
    for i, line in enumerate(lines):
        if line.startswith('+'):
            current_block.append((i + 1, line))  # Store line number and content
        elif current_block:
            # If we hit a non-added line and there's an active block, finalize it
            start_line = max(0, current_block[0][0] - context_lines - 1)
            end_line = min(len(lines) - 1, current_block[-1][0] + context_lines - 1)
            
            # Capture the lines for the block including context
            block_with_context = lines[start_line:end_line + 1]
            code_blocks.append((start_line, block_with_context))
            current_block = []

    # If there's any remaining block, append it
    if current_block:
        start_line = max(0, current_block[0][0] - context_lines - 1)
        end_line = min(len(lines) - 1, current_block[-1][0] + context_lines - 1)
        block_with_context = lines[start_line:end_line + 1]
        code_blocks.append((start_line, block_with_context))

    return code_blocks

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

    # Get the number of context lines to include above and below code block if add_inline_comments enabled (default is 0)
    context_lines = int(os.getenv('CONTEXT_LINES', 0))

    if add_inline_comments:
        for file in files:
            if file.status in ['added', 'modified']:
                # Group consecutive added/modified lines into code blocks, with context
                code_blocks = group_code_blocks(file.patch, context_lines)

                for block_start_line, block_with_context in code_blocks:
                    # Prepare the prompt for each code block with context
                    block_lines = "\n".join(block_with_context)
                    prompt = f"Review this code change in file {file.filename} with the following context:\n{block_lines}\n\nIf no issues add #looksgood."

                    # Get the response from OpenAI for this block
                    response = get_openai_response(prompt)

                    # Check if 'choices' exists in the response
                    if 'choices' in response and len(response['choices']) > 0:
                        feedback = response['choices'][0]['message']['content']
                        # Only post a comment if there's feedback beyond a looksgood response
                        if "#looksgood" not in feedback.lower() and feedback.strip():
                            # Post the feedback as an inline comment on the first line of the block
                            post_inline_comment(repo, pr, file.filename, block_start_line + 1, feedback)
                        else:
                            print("No significant issues found, no comment added.")
                    else:
                        print(f"No valid response for block starting at line {block_start_line + 1} in {file.filename}")

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
