import configparser
import webbrowser
from datetime import timedelta, datetime
from typing import Dict, Union

import requests
from flask import Flask, request

# Read settings
config = configparser.ConfigParser()
settings_file = 'sid/settings.ini'
config.read(settings_file)

# OAuth 2.0 Credentials
CLIENT_ID = config['ENV']['CLIENT_ID']
CLIENT_SECRET = config['ENV']['CLIENT_SECRET']
REDIRECT_URI = config['ENV']['REDIRECT_URI']
AUTHORIZATION_URL = config['ENV']['AUTHORIZATION_URL']
TOKEN_URL = config['ENV']['TOKEN_URL']

app = Flask(__name__)

# Global variable to store the authorization code
_auth_code = None

VERBOSE = False

def print_verbose(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)

def run_flask_app():
    app.run(port=8000)


@app.route('/callback')
def callback():
    global _auth_code
    _auth_code = request.args.get('code')
    if _auth_code:
        return "Authorization successful! You can close this window."
    else:
        return "Authorization failed!", 400


def set_tokens(access_token, refresh_token, expires_in):
    """Save the tokens to settings.ini."""
    access_token_expiry_time = datetime.now() + timedelta(seconds=expires_in)
    config['AUTH']['access_token'] = access_token
    config['AUTH']['refresh_token'] = refresh_token
    config['AUTH']['access_token_expiry_time'] = str(int(access_token_expiry_time.timestamp()))
    with open(settings_file, 'w') as configfile:
        config.write(configfile)


def get_access_token():
    """Retrieve the access token from settings.ini. This is only doing basic validation."""
    print_verbose('Retrieving access token...')
    access_token = config['AUTH']['access_token']
    access_token_expiry_time = config['AUTH']['access_token_expiry_time']
    if access_token:
        print_verbose('Access token found in settings.ini')
        print_verbose(f'Current time: {datetime.now().timestamp()}, expiry time: {float(access_token_expiry_time)}.')
        if access_token_expiry_time and datetime.now().timestamp() < float(access_token_expiry_time):
            print_verbose('Access token is still valid. No need to refresh.')
            return access_token
        else:
            print_verbose('Access token has expired. Refreshing...')
            return refresh_access_token()
    else:
        print_verbose('Access token not found in settings.ini.')
        return full_auth_flow()


def refresh_access_token():
    """Refresh the access token using the refresh token."""
    print_verbose('Refreshing access token...')
    refresh_token = config['AUTH']['refresh_token']
    try:
        if refresh_token:
            print_verbose('Refresh token found in settings.ini')
            response = requests.post(TOKEN_URL, data={
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
            })
            if response.status_code == 200:
                print_verbose('Refresh successful')
                tokens = response.json()
                set_tokens(tokens['access_token'], refresh_token, tokens['expires_in'])
                return tokens['access_token']
            else:
                raise Exception('Refresh failed')
    except Exception as e:
        print_verbose('Refresh failed')
        return full_auth_flow()

def full_auth_flow():
    print_verbose('Initiating full auth flow...')
    # Step 1: Start the Flask app in a separate thread
    import threading

    thread = threading.Thread(target=run_flask_app)
    thread.start()

    # Step 2: Get the authorization code
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'query:data+offline_access'
    }
    auth_url = f'{AUTHORIZATION_URL}?{"&".join([f"{key}={value}" for key, value in params.items()])}'
    webbrowser.open(auth_url)

    # Wait for the authorization code to be captured by the Flask app
    while _auth_code is None:
        pass

    # Step 3: Exchange the authorization code for an access token and refresh token
    response = requests.post(TOKEN_URL, data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': _auth_code,
        'grant_type': 'authorization_code',
    })
    tokens = response.json()

    # Step 4: Save the tokens to the settings file
    set_tokens(tokens['access_token'], tokens['refresh_token'], tokens['expires_in'])

    return tokens['access_token']

def make_authenticated_request(url: str, data: Dict[str, Union[str, int]], method: str = 'post') -> Dict:
    def authenticated_request(url, headers, data):
        if method == 'post':
            return requests.post(url, json=data, headers=headers)
        else:
            raise Exception('Method not supported')

    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'  # Specify that we're sending JSON data
    }
    response = authenticated_request(url, headers, data)
    if response.status_code != 200:
        access_token = refresh_access_token()
        headers['Authorization'] = f'Bearer {access_token}'
        response = authenticated_request(url, headers, data)
    return response.json()

def query_sid(query: str, limit: int = 10, context_size: int = 0,
              query_processing: Union['standard', 'extended'] = 'standard'):
    """Query the SID API."""
    data = {
        "query": query,
        "limit": limit,
        "context_size": context_size,
        "query_processing": query_processing
    }
    return make_authenticated_request('https://api.sid.ai/v1/users/me/query', data)

def example_sid(usage: Union['question', 'task'] = 'question'):
    """Example endpoint."""
    data = {
        "usage": usage
    }
    return make_authenticated_request('https://api.sid.ai/v1/users/me/example', data)