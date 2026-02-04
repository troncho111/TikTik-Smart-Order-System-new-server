import os
import base64
import json
import requests

def get_access_token():
    """Get GitHub access token from Replit connector"""
    hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
    x_replit_token = None
    
    if os.environ.get('REPL_IDENTITY'):
        x_replit_token = 'repl ' + os.environ.get('REPL_IDENTITY')
    elif os.environ.get('WEB_REPL_RENEWAL'):
        x_replit_token = 'depl ' + os.environ.get('WEB_REPL_RENEWAL')
    
    if not x_replit_token:
        raise Exception('X_REPLIT_TOKEN not found')
    
    response = requests.get(
        f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=github',
        headers={
            'Accept': 'application/json',
            'X_REPLIT_TOKEN': x_replit_token
        }
    )
    
    data = response.json()
    connection = data.get('items', [{}])[0]
    settings = connection.get('settings', {})
    
    access_token = settings.get('access_token') or settings.get('oauth', {}).get('credentials', {}).get('access_token')
    
    if not access_token:
        raise Exception('GitHub not connected')
    
    return access_token

def get_github_username(token):
    """Get authenticated user's GitHub username"""
    response = requests.get(
        'https://api.github.com/user',
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json'
        }
    )
    if response.status_code == 200:
        return response.json().get('login')
    return None

def create_repo(token, repo_name):
    """Create a new GitHub repository"""
    response = requests.post(
        'https://api.github.com/user/repos',
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json'
        },
        json={
            'name': repo_name,
            'description': 'TikTik Smart Order System - Professional Hebrew RTL PDF generation for event tickets',
            'private': False,
            'auto_init': False
        }
    )
    
    if response.status_code == 201:
        return response.json()
    elif response.status_code == 422:
        print(f"Repository may already exist: {response.json()}")
        return {'exists': True}
    else:
        print(f"Error creating repo: {response.status_code} - {response.text}")
        return None

if __name__ == '__main__':
    try:
        token = get_access_token()
        print(f"Got access token")
        
        username = get_github_username(token)
        print(f"GitHub username: {username}")
        
        repo_name = "TikTik-Smart-Order-System"
        result = create_repo(token, repo_name)
        
        if result:
            print(f"Repository ready: {username}/{repo_name}")
        else:
            print("Failed to create repository")
            
    except Exception as e:
        print(f"Error: {e}")
