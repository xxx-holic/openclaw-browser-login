# openclaw-browser-login

Give your OpenClaw agent a persistent, login-ready browser. One-time setup, permanent login state.

## What this does

- Enables OpenClaw's managed Chrome browser (openclaw profile)
- User logs in once → agent can operate any platform with that login state forever
- Adds browser operation rules to your agent's workspace (snapshot before interact, verify after)

## Quick Install

### 1. Enable browser

```bash
openclaw config set browser.enabled true
openclaw config set tools.profile '"full"'
```

### 2. Add browser rules to your workspace

Copy `BROWSER-RULES.md` content into your agent's `TOOLS.md` and `AGENTS.md`:

**Append to TOOLS.md:**
```
# Browser

You have a dedicated Chrome browser (openclaw profile). Full GUI, not headless.
Any platform the user asks you to operate is already logged in. Do not question it.

browser tool actions: navigate, snapshot, screenshot, click, type, fill, press, drag, hover, select, upload, download, evaluate, console, requests, cookies, pdf.

Workflow: snapshot (get ref IDs) → interact → snapshot (verify).
On failure: fall back to web_fetch for read-only content.
```

**Append to AGENTS.md:**
```
# Browser

You have a dedicated Chrome browser (openclaw profile). Full GUI, not headless.
When the user asks you to operate any platform requiring login, the browser is already logged in. Do not question the login state or ask for credentials.

User says "打开/open/看看/browse" → use browser, not web_fetch.
Before browser interaction: snapshot to get page structure and ref IDs.
After browser state change: snapshot or screenshot to verify.
Browser fails → fall back to web_fetch for read-only content.
```

### 3. Start gateway and log in (one-time)

1. Start your gateway: `openclaw gateway` (or however you normally start it)
2. In TG, tell your agent: `打开 x.com` (or any site you want to log in to)
3. Agent will launch Chrome — you'll see the window on your screen
4. Log in to your accounts in that Chrome window
5. Done. Login state persists in `~/.openclaw/browser/openclaw/user-data/`

## How it works

OpenClaw manages its own Chrome instance with a dedicated user-data directory (`~/.openclaw/browser/openclaw/user-data/`). When you log in through this Chrome, cookies are saved to that directory. Every time the agent uses the browser, it starts Chrome with the same directory → same login state.

## Important

- **Do NOT force-kill Chrome** (e.g., `kill -9` or Task Manager → End Process Tree). Close normally so cookies flush to disk.
- **Do NOT open Chrome manually** with the same user-data directory while the agent is using it. Only one Chrome instance can use a directory at a time.
- The agent's Chrome is completely separate from your personal Chrome.

## Tested with

- OpenClaw 2026.3.13
- Linux (Ubuntu) + Windows 11
- X/Twitter, GitHub, ChatGPT, Google verified working

## License

MIT
