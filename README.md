AI-SOC Email Triage & Forensics

This project is a Python-based tool for security analysts who need to handle suspicious emails quickly and safely. It parses .eml files, extracts headers, bodies, and attachments into structured JSON, and then uses Google Gemini to analyze the data for phishing indicators, anomalies, and potential threats.

The idea is to reduce repetitive manual triage work in SOC and DFIR investigations, while keeping the workflow transparent and reproducible.

Features

Parse .eml email files with Python’s email library

Extract headers, plain text, HTML, and attachments

Store everything in JSON format for easy review and downstream use

Attachments stored in Base64 to avoid accidental execution

Send structured email data to Gemini for offline-style phishing/threat analysis

Designed for SOC, DFIR, and incident response use cases

Setup

Clone the repo

git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>


Install dependencies

pip install -r requirements.txt


Set your API key

Create a .env file in the project root:

GOOGLE_API_KEY=your_api_key_here


Or set it as an environment variable (setx GOOGLE_API_KEY "your_api_key_here" on Windows).

Usage

Place your .eml files in a folder, e.g.:

C:\Users\dhire\Documents\phishing_pot\test


Run the analyzer:

python email_analyzer.py


Output:

Parsed JSON file: eml_data_output.json

Gemini analysis printed in terminal

Example Workflow

SOC analyst downloads a suspicious email as .eml

Run this tool to safely extract headers, body, and attachments

Use Gemini’s analysis to flag impersonation, phishing lures, or abnormal headers

Store the JSON output for case documentation

Disclaimer

This project is for educational and research purposes. It does not execute attachments or external links, but always handle real phishing emails in a safe lab environment.
