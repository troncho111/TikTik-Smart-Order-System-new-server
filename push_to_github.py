import os
import base64
import json
import requests
import time

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

# Files to upload
FILES_TO_UPLOAD = [
    'app.py',
    'models.py',
    'pdf_generator.py',
    'passport_ocr.py',
    'hotel_resolver.py',
    'flight_ocr.py',
    'concert_ocr.py',
    'concerts_service.py',
    'concerts_data.py',
    'exchange_rates.py',
    'airports.py',
    'stadium_api.py',
    'sports_api.py',
    'main.py',
    'terms.txt',
    'pyproject.toml',
    'replit.md',
    'DOCUMENTATION.md',
    'teams_stadiums_mapping.json',
    'worldcup2026.json',
    'worldcup_stadiums_mapping.json',
    'pages/signature.py',
    'templates/order_template_2.html',
    'fonts/Arial.ttf',
    'assets/logo.png',
    'assets/signature_placeholder.png',
    'logo.png',
    'logo_original.png',
    'header_banner.png',
    'cover_page.png',
    'concert_background.png',
    'Dockerfile',
    'railway.json',
    '.streamlit/config.toml',
]

# Directories to upload
DIRS_TO_SCAN = ['stadium_maps', 'templates', 'pages', 'fonts', 'assets']

def get_all_files():
    """Get all files to upload"""
    files = []
    
    # Add specific files
    for f in FILES_TO_UPLOAD:
        if os.path.exists(f):
            files.append(f)
    
    # Scan directories
    for dir_name in DIRS_TO_SCAN:
        if os.path.exists(dir_name):
            for root, dirs, filenames in os.walk(dir_name):
                # Skip __pycache__
                dirs[:] = [d for d in dirs if d != '__pycache__']
                for filename in filenames:
                    if not filename.endswith('.pyc'):
                        filepath = os.path.join(root, filename)
                        if filepath not in files:
                            files.append(filepath)
    
    return list(set(files))

def upload_file(token, owner, repo, filepath):
    """Upload a single file to GitHub (create or update)"""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        content_b64 = base64.b64encode(content).decode('utf-8')
        
        existing_sha = None
        check_response = requests.get(
            f'https://api.github.com/repos/{owner}/{repo}/contents/{filepath}',
            headers={
                'Authorization': f'Bearer {token}',
                'Accept': 'application/vnd.github+json'
            }
        )
        if check_response.status_code == 200:
            existing_sha = check_response.json().get('sha')
        
        payload = {
            'message': f'Update {filepath}' if existing_sha else f'Add {filepath}',
            'content': content_b64
        }
        if existing_sha:
            payload['sha'] = existing_sha
        
        response = requests.put(
            f'https://api.github.com/repos/{owner}/{repo}/contents/{filepath}',
            headers={
                'Authorization': f'Bearer {token}',
                'Accept': 'application/vnd.github+json'
            },
            json=payload
        )
        
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"  Error uploading {filepath}: {response.status_code}")
            return False
    except Exception as e:
        print(f"  Exception uploading {filepath}: {e}")
        return False

def create_requirements_txt(token, owner, repo):
    """Create requirements.txt"""
    requirements = """arabic-reshaper>=3.0.0
bcrypt>=4.0.0
beautifulsoup4>=4.12.0
cairosvg>=2.7.0
extra-streamlit-components>=0.1.60
fpdf>=1.7.2
fpdf2>=2.7.0
google-genai>=1.0.0
jinja2>=3.1.0
lxml>=5.0.0
openpyxl>=3.1.0
pillow>=10.0.0
playwright>=1.40.0
psycopg2-binary>=2.9.0
python-bidi>=0.4.2
requests>=2.31.0
resend>=0.8.0
sift-stack-py>=0.9.0
sqlalchemy>=2.0.0
streamlit>=1.29.0
streamlit-drawable-canvas>=0.9.0
streamlit-paste-button>=0.1.0
weasyprint>=60.0
"""
    
    content_b64 = base64.b64encode(requirements.encode()).decode('utf-8')
    
    existing_sha = None
    check_response = requests.get(
        f'https://api.github.com/repos/{owner}/{repo}/contents/requirements.txt',
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json'
        }
    )
    if check_response.status_code == 200:
        existing_sha = check_response.json().get('sha')
    
    payload = {
        'message': 'Update requirements.txt',
        'content': content_b64
    }
    if existing_sha:
        payload['sha'] = existing_sha
    
    response = requests.put(
        f'https://api.github.com/repos/{owner}/{repo}/contents/requirements.txt',
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json'
        },
        json=payload
    )
    
    return response.status_code in [200, 201]

if __name__ == '__main__':
    token = get_access_token()
    owner = 'troncho111'
    repo = 'TikTik-Smart-Order-System'
    
    files = get_all_files()
    print(f"Found {len(files)} files to upload")
    
    # Create requirements.txt first
    print("Creating requirements.txt...")
    create_requirements_txt(token, owner, repo)
    
    # Upload files
    success = 0
    failed = 0
    for i, filepath in enumerate(files):
        print(f"[{i+1}/{len(files)}] Uploading {filepath}...")
        if upload_file(token, owner, repo, filepath):
            success += 1
        else:
            failed += 1
        time.sleep(0.3)  # Rate limit
    
    print(f"\nDone! Success: {success}, Failed: {failed}")
    print(f"Repository: https://github.com/{owner}/{repo}")
