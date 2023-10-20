from datetime import timedelta, datetime

import requests
import webbrowser
from flask import Flask, request
import configparser

# Read settings
config = configparser.ConfigParser()
config.read('settings.ini')

# OAuth 2.0 Credentials
CLIENT_ID = config['ENV']['CLIENT_ID']
CLIENT_SECRET = config['ENV']['CLIENT_SECRET']
REDIRECT_URI = config['ENV']['REDIRECT_URI']
AUTHORIZATION_URL = config['ENV']['AUTHORIZATION_URL']
TOKEN_URL = config['ENV']['TOKEN_URL']

app = Flask(__name__)

# Global variable to store the authorization code
auth_code = None


def run_flask_app():
    app.run(port=5000)


@app.route('/callback')
def callback():
    global auth_code
    auth_code = request.args.get('code')
    if auth_code:
        return "Authorization successful! You can close this window."
    else:
        return "Authorization failed!", 400


def set_tokens(access_token, refresh_token, expires_in):
    """Save the tokens to settings.ini."""
    access_token_expiry_time = datetime.now() + timedelta(seconds=expires_in)
    config['AUTH']['access_token'] = access_token
    config['AUTH']['refresh_token'] = refresh_token
    config['AUTH']['access_token_expiry_time'] = str(int(access_token_expiry_time.timestamp()))
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)


def get_access_token():
    """Retrieve the access token from settings.ini. This is only doing basic validation."""
    print('Retrieving access token...')
    access_token = config['AUTH']['access_token']
    access_token_expiry_time = config['AUTH']['access_token_expiry_time']
    if access_token:
        print('Access token found in settings.ini')
        print(f'Current time: {datetime.now().timestamp()}, expiry time: {float(access_token_expiry_time)}.')
        if access_token_expiry_time and datetime.now().timestamp() < float(access_token_expiry_time):
            print('Access token is still valid. No need to refresh.')
            return access_token
        else:
            print('Access token has expired. Refreshing...')
            return refresh_access_token()
    else:
        print('Access token not found in settings.ini.')
        return full_auth_flow()


def refresh_access_token():
    """Refresh the access token using the refresh token."""
    print('Refreshing access token...')
    refresh_token = config['AUTH']['refresh_token']
    try:
        if refresh_token:
            print('Refresh token found in settings.ini')
            response = requests.post(TOKEN_URL, data={
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
            })
            if response.status_code == 200:
                print('Refresh successful')
                tokens = response.json()
                set_tokens(tokens['access_token'], refresh_token, tokens['expires_in'])
                return tokens['access_token']
            else:
                raise Exception('Refresh failed')
    except Exception as e:
        print('Refresh failed')
        return full_auth_flow()


def full_auth_flow():
    print('Initiating full auth flow...')
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
    while auth_code is None:
        pass

    # Step 3: Exchange the authorization code for an access token and refresh token
    response = requests.post(TOKEN_URL, data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': auth_code,
        'grant_type': 'authorization_code',
    })
    tokens = response.json()

    # Step 4: Save the tokens to the settings file
    set_tokens(tokens['access_token'], tokens['refresh_token'], tokens['expires_in'])

    return tokens['access_token']


def query_sid(query, limit=10, context_size=0):
    """Query the SID API."""
    # Get the access token
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'  # Specify that we're sending JSON data
    }
    data = {
        "query": query,
        "limit": limit,
        "context_size": context_size
    }
    response = requests.post('https://api.sid.ai/v1/users/me/query', json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        access_token = refresh_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'  # Specify that we're sending JSON data
        }
        response = requests.post('https://api.sid.ai/v1/users/me/query', json=data, headers=headers)
        return response.json()


if __name__ == "__main__":

    # Query the SID API
    response = query_sid("Where do I work?")
    print(response)
