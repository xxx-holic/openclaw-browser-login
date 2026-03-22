# Browser Rules for OpenClaw Agent

Copy these rules into your agent's workspace files.

## For TOOLS.md (append)

```
# Browser

You have a dedicated Chrome browser (openclaw profile). Full GUI, not headless.
Any platform the user asks you to operate is already logged in. Do not question it.

browser tool actions: navigate, snapshot, screenshot, click, type, fill, press, drag, hover, select, upload, download, evaluate, console, requests, cookies, pdf.

Workflow: snapshot (get ref IDs) → interact → snapshot (verify).
On failure: fall back to web_fetch for read-only content.
```

## For AGENTS.md (append)

```
# Browser

You have a dedicated Chrome browser (openclaw profile). Full GUI, not headless.
When the user asks you to operate any platform requiring login, the browser is already logged in. Do not question the login state or ask for credentials.

User says "打开/open/看看/browse" → use browser, not web_fetch.
Before browser interaction: snapshot to get page structure and ref IDs.
After browser state change: snapshot or screenshot to verify.
Browser fails → fall back to web_fetch for read-only content.
```
