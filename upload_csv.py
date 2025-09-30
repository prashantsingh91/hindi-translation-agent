#!/usr/bin/env python3
"""
Script to upload the complete CSV file to GitHub
"""

import requests
import base64
import json
import os

def upload_csv_to_github():
    # Read the complete CSV file
    with open('complete_hospitals.csv', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encode content to base64
    content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    # GitHub API endpoint
    url = "https://api.github.com/repos/prashantsingh91/hindi-translation-agent/contents/ui/hospitals_hindi_names_degenericized.csv"
    
    # Headers
    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Data payload
    data = {
        "message": "Upload complete healthcare facilities dataset with 1,155+ entries",
        "content": content_b64,
        "branch": "main"
    }
    
    # Make the request
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("✅ CSV file uploaded successfully!")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Upload failed with status code: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    upload_csv_to_github()
