# AI Pull Request Reviewer

This repository contains GitHub Action scripts that utilize AI (such as OpenAI's GPT-4) to automatically review pull requests and respond to comments on pull requests. This can help maintain code quality and provide insightful feedback during code reviews.

## Features

- **Automated Code Reviews**: Automatically review code changes when a pull request is created.
- **AI-Powered Comment Responses**: Respond to pull request comments with AI-generated feedback when prompted by `@pr-ai`.
- **Easy Integration**: Integrate into any GitHub project by installing as an npm module or copying the necessary files.

## Requirements

- **Node.js**: Version 18 or higher might be required to run the installation script and dependencies.

## Installation

You can integrate this GitHub Action into your project in three ways:

### Option 1: Install via npm with Auto-Copy (Recommended)

1. **Install via npx**: Run the following command to pull the module with npx install the necessary files:

```bash
npx https://github.com/librispark/AI-PR-reviewer
```
This will execute the installation script and copy the files to your project.

2. **Configure Your Repository**: Ensure your repository has the necessary environment variables configured (see below).

3. **Install the Module via npm**: 
Run the following command to install the module and it should install the module and automatically copy the necessary files, if the files aren't copied it will need to be done manually:

```bash
npm install https://github.com/librispark/AI-PR-reviewer
```

This will automatically copy the ai_code_review.yml file to .github/workflows/ and the ai_code_review.py and respond_to_comment.py files to .github/scripts/.

### Option 2: Install via npm (Manual Copy)
1. **Install the Module**: First, add this module to your project as a dependency. If the module is published to npm, use the following command:

```bash
npm install https://github.com/librispark/AI-PR-reviewer
```

2. **Add Workflow to Your Project**: Copy the provided GitHub workflow and script files to your project:

```bash
cp -r node_modules/ai-pr-reviewer/ai_code_review.yml .github/workflows/
cp -r node_modules/ai-pr-reviewer/ai_code_review.py .github/scripts/
cp -r node_modules/ai-pr-reviewer/respond_to_comment.py .github/scripts/
```

3. **Configure Your Repository**: Ensure your repository has the necessary environment variables configured (see below).

### Option 3: Manual Installation
1. **Clone or Download**: Clone this repository or download the necessary files.

```bash
git clone https://github.com/librispark/AI-PR-reviewer
```

2. **Copy Files to Your Project**: Copy the ai_code_review.yml, ai_code_review.py, and respond_to_comment.py files to the appropriate directories in your project:

```bash
cp ai_code_review.yml .github/workflows/
cp ai_code_review.py .github/scripts/
cp respond_to_comment.py .github/scripts/
```

3. **Configure Your Repository**: Ensure your repository has the necessary environment variables configured (see below).

## Required Environment Variables

To use this GitHub Action, you need to configure the following environment variables in your repository settings:

### `GITHUB_TOKEN`

- **Description**: A token that GitHub Actions automatically provides to authenticate workflows. It allows the action to interact with the GitHub API to post comments on pull requests.
- **Setup**: This token is automatically available in GitHub Actions, so no additional configuration is necessary.

### `OPENAI_API_KEY`

- **Description**: Your API key for accessing OpenAI's GPT model. This key is required for generating AI-powered responses and code reviews.
- **Setup**: You need to obtain an API key from OpenAI and add it to your repository secrets:
  1. Go to your GitHub repository.
  2. Navigate to `Settings` > `Secrets` > `Actions`.
  3. Click `New repository secret`.
  4. Name the secret `OPENAI_API_KEY` and paste your OpenAI API key into the value field.

### `ADD_INLINE_COMMENTS`

- **Description**: This variable controls whether the AI makes multiple API calls to review each individual code change in a pull request. When set to `true`, the AI will review each code block or line change separately and provide feedback by posting inline comments. If set to `false`, inline comments won't run (default).
- **Default**: `false`
- **Possible Values**:
  - `true`: The AI will review each code change individually and provide inline feedback for each modification.
  - `false`: The AI will skip the inline comments.
- **Setup**: You need to add it to your repository variables:
  1. Go to your GitHub repository.
  2. Navigate to `Settings` > `Secrets` > `Actions`.
  3. Click `New repository variable`.
  4. Name the secret `ADD_INLINE_COMMENTS` and paste `true` or `false` into the value field.

### `ADD_WHOLE_PR_COMMENT`

- **Description**: This variable controls whether the AI posts a summary comment for the entire pull request. When set to `true`, the AI will provide a general comment summarizing the feedback for the entire PR. When set to `false`, the summary comment will be skipped, and feedback will only be provided inline (if `ADD_INLINE_COMMENTS` is enabled).
- **Default**: `true`
- **Possible Values**:
  - `true`: The AI will post a summary comment for the whole pull request.
  - `false`: The AI will skip the summary comment.
- **Setup**: You need to add it to your repository variables (same as above).

## Usage

Once installed, the GitHub Actions will automatically trigger when:

- **A Pull Request is Created**: The action will review the code changes and add comments with feedback.
- **A Comment Contains `@pr-ai`**: The action will respond to the comment with AI-generated feedback, considering the context of the entire conversation.

## Customization

You can customize the AI behavior by modifying the Python scripts:

- **`ai_code_review.py`**: Handles the AI-driven code review when a pull request is opened.
- **`respond_to_comment.py`**: Handles the AI response when a comment includes `@pr-ai`.
