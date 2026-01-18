import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
from urllib.parse import urlparse, parse_qs

# ✅ حط الـ credentials بتوعك هنا
APP_KEY = 'wdrpx3zjlqbpie3'
APP_SECRET = '3dt8bvozgy4rjae'

# OAuth URLs
AUTH_URL = 'https://www.dropbox.com/oauth2/authorize'
TOKEN_URL = 'https://api.dropbox.com/oauth2/token'
REDIRECT_URI = 'http://localhost:5000/dropbox-auth-callback'

# Global variable to store auth code
auth_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        
        # Parse the authorization code from callback
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if 'code' in params:
            auth_code = params['code'][0]
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''            ''')
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Error: No authorization code received</h1>')
    
    def log_message(self, format, *args):
        pass  # Suppress server logs

def get_refresh_token():
    print("🚀 Starting Dropbox OAuth Flow...")
    print(f"📝 App Key: {APP_KEY}")
    print(f"📝 Redirect URI: {REDIRECT_URI}")
    
    # Step 1: Generate authorization URL
    auth_url = (
        f"{AUTH_URL}?"
        f"client_id={APP_KEY}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"response_type=code&"
        f"token_access_type=offline"  # ✅ This gives us refresh token
    )
    
    print("\n📌 Opening browser for authorization...")
    print(f"🔗 URL: {auth_url}\n")
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Start local server to receive callback
    print("🌐 Starting local server on http://localhost:5000")
    print("⏳ Waiting for authorization...\n")
    
    server = HTTPServer(('localhost', 5000), OAuthHandler)
    
    # Wait for one request (the callback)
    server.handle_request()
    
    if not auth_code:
        print("❌ Failed to get authorization code")
        return None
    
    print(f"✅ Authorization code received: {auth_code[:20]}...\n")
    
    # Step 2: Exchange auth code for refresh token
    print("🔄 Exchanging code for tokens...")
    
    data = {
        'code': auth_code,
        'grant_type': 'authorization_code',
        'client_id': APP_KEY,
        'client_secret': APP_SECRET,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post(TOKEN_URL, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        
        print("\n" + "="*60)
        print("🎉 SUCCESS! Your Dropbox Tokens:")
        print("="*60)
        print(f"\n📝 Access Token (expires in ~4 hours):")
        print(f"   {tokens['access_token']}\n")
        print(f"🔑 Refresh Token (keep this secure!):")
        print(f"   {tokens['refresh_token']}\n")
        print("="*60)
        
        print("\n✅ Add these to your .env file:")
        print(f"\nDROPBOX_APP_KEY={APP_KEY}")
        print(f"DROPBOX_APP_SECRET={APP_SECRET}")
        print(f"DROPBOX_REFRESH_TOKEN={tokens['refresh_token']}\n")
        
        return tokens
    else:
        print(f"❌ Failed to get tokens: {response.status_code}")
        print(f"📄 Response: {response.text}")
        return None

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔐 Dropbox OAuth Token Generator")
    print("="*60 + "\n")
    
    # Verify credentials
    if APP_KEY == 'YOUR_APP_KEY_HERE' or APP_SECRET == 'YOUR_APP_SECRET_HERE':
        print("❌ Error: Please update APP_KEY and APP_SECRET in the script!")
        print("\n📍 Get them from: https://www.dropbox.com/developers/apps")
        exit(1)
    
    get_refresh_token()
