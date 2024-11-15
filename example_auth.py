import requests
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import jwt
from jwt import PyJWKClient

# Configuration
client_id = 'your_client_id'
client_secret = 'your_client_secret'
# redirect_uri = 'http://localhost:8080/callback'
scopes = 'openid profile email'
authorization_url = "http://localhost:8080/default/authorize"
well_known_url = "http://localhost:8080/default/jwks"
token_url = "http://localhost:8080/default/token"
userinfo_url = "http://localhost:8080/default/userinfo"
username = "test@test.com"
password = "test"
audience = client_id 
claims = {}  # Additional claims to request.
local_capture_port = 3001

# Local Server to Capture Authorization Code
class AuthHandler(BaseHTTPRequestHandler):
    authorization_code = None

    def do_GET(self):
        # Parse query parameters from the URL
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        # Capture the "code" parameter
        if 'code' in params:
            AuthHandler.authorization_code = params['code'][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this window.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed! Missing 'code' parameter.")

    @staticmethod
    def start_server():
        server = HTTPServer(('localhost', local_capture_port), AuthHandler)
        print("Listening on http://localhost:{}/callback for the authorization code...".format(local_capture_port))
        server.handle_request()  # Handle a single request and then stop

# Step 1: Capture Authorization Code
def get_authorization_code():
    # Start the local server in a separate thread to capture the code
    server_thread = threading.Thread(target=AuthHandler.start_server, daemon=True)
    server_thread.start()

    # Open the authorization URL in a browser or print the URL to manually open
    params = {
        'client_id': client_id,
        'redirect_uri': 'http://localhost:{}/callback'.format(local_capture_port),
        'response_type': 'code',
        'scope': scopes
    }

    data = {
        'username': username,
        'claims': claims
    }

    response = requests.post(authorization_url, params=params, data=data)

    if response.status_code != 200:
        raise Exception("{} when trying to authorize: {}".format(response.status_code, response.content))

    # Wait for the authorization code to be captured
    server_thread.join()

    # Return the captured authorization code
    if AuthHandler.authorization_code:
        print("Authorization code received:", AuthHandler.authorization_code)
        return AuthHandler.authorization_code
    else:
        raise Exception("Failed to obtain authorization code")

# Step 2: Exchange Authorization Code for Access Token
def get_access_token(auth_code):
    # Start the local server in a separate thread to capture the code
    # Starting it as a daemon will kill it when this script finishes executing
    server_thread = threading.Thread(target=AuthHandler.start_server, daemon=True)
    server_thread.start()

    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(token_url, data=data, headers=headers)

    if response.ok:
        token_data = response.json()
        print(token_data)
        access_token = token_data.get('access_token')
        my_jwt = token_data.get('id_token')
        print("Access Token:", access_token)
        print("JWT:", my_jwt)

        jwks_client = PyJWKClient(well_known_url)
        signing_key = jwks_client.get_signing_key_from_jwt(my_jwt)

        print("Decoded JWT:", jwt.decode(my_jwt, signing_key.key, audience=audience, algorithms=["RS256"]))
        
        return access_token
    else:
        raise Exception("Failed to get access token:", response.text)

# User Info.
# Step 3: Fetch User Info (Optional)
def fetch_user_info(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(userinfo_url, headers=headers)
    if response.ok:
        print("User Info:", response.json())
    else:
        print("Failed to get user info:", response.status_code, response.text)

# Run the flow
if __name__ == "__main__":
    try:
        # Get authorization code
        auth_code = get_authorization_code()
        if auth_code:
            # Exchange code for token
            token = get_access_token(auth_code)

            # Get user info.
            fetch_user_info(token)
    except Exception as e:
        print("Error:", e)
