---
name: "browser-login"
description: "Operate the browser with persistent login state. Navigate, click, fill, post — on any platform the user has logged into. Triggers on: browser operations, '打开/open/browse', social media posting, form filling, web scraping, or any task requiring a logged-in browser."
user-invocable: true
disable-model-invocation: false
---

# Browser Login — Persistent Login State Browser Operations

You have a dedicated Chrome browser managed by OpenClaw (openclaw profile).
It is a full GUI browser, NOT headless. The user can see it on their screen.
Login state persists across sessions in `~/.openclaw/browser/openclaw/user-data/`.

## First-Time Setup Check

Before any browser operation, verify the browser is configured:

```bash
openclaw config get browser.enabled
openclaw config get tools.profile
```

If `browser.enabled` is not `true` or `tools.profile` is not `"full"`, run:

```bash
openclaw config set browser.enabled true
openclaw config set tools.profile '"full"'
```

Then tell the user:

"Browser is now enabled. I need you to do these one-time steps:
1. I'll open a Chrome window now — in that Chrome, go to chrome://inspect/#remote-debugging
2. Check the box 'Allow remote debugging for this browser instance'
3. Then log in to any platforms you want me to operate (X, GitHub, etc.)
4. Tell me when done."

## Login State

- The browser uses a dedicated user-data directory. Cookies persist.
- If the user has already logged in, DO NOT ask for credentials or question the login state.
- If a page shows a login screen, tell the user: "You're not logged in to [platform] in my browser. Please log in now in the Chrome window, then tell me when done."
- NEVER attempt to fill in login credentials yourself.

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
4. If browser fails or times out: fall back to `web_fetch` for read-only content. Report the failure.
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
2. Snapshot first to get ref IDs
3. Use `browser screenshot ref="ref_xxx"` targeting the main content element — do NOT screenshot the full page
4. NEVER send a full-viewport screenshot. Always target a specific element ref. Full-page screenshots produce unusable images with large blank areas.
