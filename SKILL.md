---
name: "browser-login"
description: "Operate the browser with persistent login state. Navigate, click, fill, post — on any platform the user has logged into. Triggers on: browser operations, '打开/open/browse', social media posting, form filling, web scraping, or any task requiring a logged-in browser."
user-invocable: true
disable-model-invocation: false
---

# Browser Login — Persistent Login State Browser Operations

CRITICAL: You already have a browser. OpenClaw manages its own Chrome automatically.
- DO NOT ask the user to start Chrome manually
- DO NOT ask the user to run Chrome with --remote-debugging-port
- DO NOT try to connect to the user's personal Chrome
- Just use the browser tool with profile="openclaw" — it works out of the box

The browser is a full GUI Chrome (NOT headless). The user can see it on their screen.
Login state persists across sessions in `~/.openclaw/browser/openclaw/user-data/`.

## First-Time Setup Check

Before the FIRST browser operation ever, verify the browser is configured:

```bash
openclaw config get browser.enabled
openclaw config get tools.profile
```

If `browser.enabled` is not `true` or `tools.profile` is not `"full"`, run:

```bash
openclaw config set browser.enabled true
openclaw config set tools.profile '"full"'
```

After enabling, use the browser tool to open any page (e.g. `browser navigate url="https://x.com" profile="openclaw"`). Chrome will start automatically. Then tell the user:

"I've opened a Chrome window. Please do these one-time steps in that window:
1. Go to chrome://inspect/#remote-debugging and check 'Allow remote debugging'
2. Log in to any platforms you want me to operate (X, GitHub, etc.)
3. Tell me when done."

After the user confirms, the browser is ready. You will never need to ask the user to start Chrome again.

## Login State

- The browser uses a dedicated user-data directory. Cookies persist.
- If the user has already logged in, DO NOT ask for credentials or question the login state.
- If a page shows a login screen, tell the user: "You're not logged in to [platform] in my browser. Please log in now in the Chrome window, then tell me when done."
- NEVER attempt to fill in login credentials yourself.

## Timeout Handling

Browser navigate/screenshot may report "timeout" but Chrome actually loaded the page successfully (user can see it on screen).

When you get a timeout error:
1. DO NOT report failure to the user
2. DO NOT fall back to web_fetch
3. Instead, try `browser snapshot` — if it returns page content, the page loaded fine
4. If snapshot also fails, try once more after 3 seconds
5. Only report failure after 3 consecutive failed attempts

## Screenshot — How to Get Clean Screenshots

Problem: `browser screenshot` defaults to capturing the ENTIRE page (fullPage), not just the visible viewport. This produces huge images with mostly blank space, especially on sites with infinite scroll.

Solution: resize viewport BEFORE taking screenshot, then use CDP to capture viewport only.

### Standard screenshot procedure:
```
# Step 1: Resize viewport to reasonable size
browser resize width=800 height=600 profile="openclaw"

# Step 2: Take screenshot (captures viewport area)
browser screenshot profile="openclaw"
```

### For element-specific screenshots:
```
# Snapshot to find element refs, then screenshot that element
browser snapshot profile="openclaw"
browser screenshot ref="ref_42" profile="openclaw"
```

### If screenshot still has blank areas (fallback — use CDP directly):
```bash
python3 -c "
import websocket, json, base64
ws = websocket.create_connection('ws://127.0.0.1:18800/devtools/page/<targetId>', suppress_origin=True)
ws.send(json.dumps({'id':1,'method':'Page.captureScreenshot','params':{'format':'jpeg','quality':90}}))
resp = json.loads(ws.recv())
with open('/tmp/screenshot.jpg','wb') as f:
    f.write(base64.b64decode(resp['result']['data']))
ws.close()
"
```
Get targetId from `browser tabs` first. CDP's Page.captureScreenshot always captures viewport only.

## Browser Operation Workflow

### Step 1: Navigate
```
browser navigate url="https://example.com" profile="openclaw"
```

### Step 2: Read page (get element refs)
```
browser snapshot profile="openclaw"
```
This returns a structured list of elements with `ref` IDs. Use these refs for interaction.

### Step 3: Interact
```
browser click ref="ref_123" profile="openclaw"
browser type ref="ref_456" text="Hello world" profile="openclaw"
browser fill ref="ref_789" value="content" profile="openclaw"
```

### Step 4: Verify
After any state-changing action, take a snapshot or screenshot to confirm the outcome:
```
browser snapshot profile="openclaw"
```

## Available Actions

navigate, snapshot, screenshot, click, type, fill, press, drag, hover, select, upload, download, evaluate, console, requests, cookies, pdf.

## Rules

1. ALWAYS use `profile="openclaw"` for all browser actions.
2. ALWAYS snapshot before interacting with elements (you need ref IDs).
3. ALWAYS verify after state-changing actions (click, fill, submit).
4. If browser times out: try `browser snapshot` to check if page actually loaded (it usually did). Only fall back to `web_fetch` after 3 consecutive failures.
5. For write operations (posting, submitting, ordering): confirm with user before clicking submit.
6. For read operations (browsing, scraping, checking): just do it, no confirmation needed.
7. NEVER force-close Chrome. Let it close naturally.
8. If page shows login screen unexpectedly: tell user to log in, don't try to authenticate.

## Common Tasks

**Post to X/Twitter:**
1. Navigate to x.com
2. Snapshot to find the post/compose button
3. Click compose, type content
4. Confirm with user before posting
5. Click post, verify success

**Fill a form:**
1. Navigate to the form page
2. Snapshot to identify all form fields and their refs
3. Fill each field using the ref IDs
4. Confirm with user before submitting
5. Submit and verify

**Read/scrape a page:**
1. Navigate to the URL
2. Snapshot to get structured text content
3. Extract and summarize the information
4. No confirmation needed — this is read-only

**Take a screenshot for the user:**
1. Navigate to the page
2. `browser snapshot` — find the main content container ref (look for article, main, feed, or the largest content block)
3. `browser screenshot ref="ref_xxx"` — screenshot ONLY that element
4. If the screenshot still has margins, find a more specific inner element ref and retry
