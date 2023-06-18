# pip install requests tqdm

import os
import requests
from tqdm import tqdm

# GitHub API endpoint for creating a file in a repository
api_endpoint = 'https://api.github.com/repos/{owner}/{repo}/contents/{path}'

# GitHub access token (retrieved from environment variable)
access_token = os.environ.get('GITHUB_API_KEY')

# Repository owner and name (retrieved from environment variables)
repository_owner = os.environ.get('GITHUB_USERNAME')
repository_name = os.environ.get('Repository')

# Source folder path on your local system
source_folder_path = r'C:\Source\Dev\Scripts to Upload'

def upload_to_github(access_token, repository_owner, repository_name, source_folder_path):
    # Set the headers with the access token
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Iterate over the files in the source folder and upload them to GitHub
    for root, dirs, files in os.walk(source_folder_path):
        for file in tqdm(files, desc='Uploading files', unit='file'):
            file_path = os.path.join(root, file)
            file_name = os.path.basename(file_path)

            # Read the file content
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Prepare the API endpoint URL with the necessary parameters
            url = api_endpoint.format(owner=repository_owner, repo=repository_name, path=file_name)

            # Prepare the request payload with the file content
            data = {
                'message': f'Upload {file_name}',
                'content': file_content.decode('utf-8')
            }

            # Send the API request to create the file in the repository
            response = requests.put(url, headers=headers, json=data)

            if response.status_code == 201:
                tqdm.write(f'Uploaded file: {file_path}')
            else:
                tqdm.write(f'Failed to upload file: {file_path}')

upload_to_github(access_token, repository_owner, repository_name, source_folder_path)
