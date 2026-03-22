# openclaw-browser-login

OpenClaw skill that gives your agent a persistent, login-ready browser. One-time setup, permanent login state.

Your agent can browse, click, fill forms, post to social media, scrape data — on any platform you've logged into.

## Install

```bash
# Clone to OpenClaw skills directory
git clone https://github.com/xxx-holic/openclaw-browser-login.git ~/.openclaw/skills/browser-login

# Run setup (enables browser in OpenClaw config)
bash ~/.openclaw/skills/browser-login/scripts/setup.sh
```

**Windows:**
```cmd
git clone https://github.com/xxx-holic/openclaw-browser-login.git %USERPROFILE%\.openclaw\skills\browser-login
openclaw config set browser.enabled true
openclaw config set tools.profile "\"full\""
```

## First-Time Login (one-time, ~2 minutes)

1. Start your gateway (`openclaw gateway`)
2. In TG, tell your agent: **"打开 x.com"** (or any site you want to operate)
3. Chrome opens on your screen — in that Chrome:
   - Go to `chrome://inspect/#remote-debugging`
   - Check **"Allow remote debugging for this browser instance"**
   - Then log in to your accounts (X, GitHub, etc.)
4. Tell your agent "登录好了" — done. Login state persists forever.

The agent's Chrome is completely separate from your personal Chrome. Your logins are stored in `~/.openclaw/browser/openclaw/user-data/`.

## Usage

After setup, just talk naturally:

| You say | Agent does |
|---------|-----------|
| "帮我在X发个推，聊聊AI" | Opens X, composes tweet, confirms before posting |
| "打开 github.com/my-repo" | Opens page in browser, reads content |
| "帮我填这个表单" | Opens form, fills fields, confirms before submit |
| "抓一下这个页面的数据" | Navigates, snapshots, extracts structured data |
| "去ChatGPT搜一下最新的AI新闻" | Opens ChatGPT, types query, reads response |

## How It Works

OpenClaw manages a dedicated Chrome instance (`openclaw` profile) with its own user-data directory. Cookies persist across restarts. The SKILL.md teaches the agent:

- **Snapshot before interact** — get element refs before clicking/typing
- **Verify after action** — confirm the outcome after state changes
- **Confirm before submit** — ask user before posting/ordering/submitting
- **Auto-fallback** — if browser fails, fall back to web_fetch for read-only content
- **Self-setup** — if browser isn't configured, agent configures it automatically

## Important

- **Do NOT force-kill Chrome** (`kill -9` / Task Manager → End Process Tree). Close normally so cookies flush to disk.
- **Do NOT manually open Chrome** with the same user-data directory while the agent is using it.
- If a site shows a login screen, the agent will ask you to log in — it never fills credentials for you.

## Tested With

- OpenClaw 2026.3.13+
- Linux (Ubuntu 22.04) + Windows 11
- X/Twitter, GitHub, ChatGPT, Google — verified working

## License

MIT
