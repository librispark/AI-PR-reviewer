#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Define source paths
const workflowFileSrc = path.join(__dirname, 'ai_code_review.yml');
const scriptFile1Src = path.join(__dirname, 'ai_code_review.py');
const scriptFile2Src = path.join(__dirname, 'respond_to_comment.py');
const reqsFileSrc = path.join(__dirname, 'requirements.txt');

// Define destination paths
const workflowFileDest = path.join(process.cwd(), '.github', 'workflows', 'ai_code_review.yml');
const scriptFile1Dest = path.join(process.cwd(), '.github', 'scripts', 'ai_code_review.py');
const scriptFile2Dest = path.join(process.cwd(), '.github', 'scripts', 'respond_to_comment.py');
const reqsFileDest = path.join(process.cwd(), '.github', 'scripts', 'requirements.txt');

// Function to ensure directory exists
function ensureDirSync(dir) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}

// Function to copy a file from source to destination
function copyFile(src, dest) {
    ensureDirSync(path.dirname(dest));
    fs.copyFileSync(src, dest);
    // console.log(`Copied ${src} to ${dest}`);
}

// Copy the workflow file
copyFile(workflowFileSrc, workflowFileDest);

// Copy the script files
copyFile(scriptFile1Src, scriptFile1Dest);
copyFile(scriptFile2Src, scriptFile2Dest);
copyFile(reqsFileSrc, reqsFileDest);

console.log('AI Code Review and Comment Responder files have been installed successfully.');
