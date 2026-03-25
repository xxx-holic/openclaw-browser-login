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

- The user has already logged in to all platforms they need you to operate (X, GitHub, food delivery, email, etc.) in your dedicated browser. Login state is persistent.
- DO NOT question login state. DO NOT ask for credentials. DO NOT ask "are you logged in?".
- If a page unexpectedly shows a login screen, it means the session expired. Tell the user: "Your [platform] session expired. Please re-login in my Chrome window." Do not try to authenticate yourself.

## Timeout Handling

CRITICAL: Browser tool often reports "timeout" on first use because Chrome startup takes time. But Chrome DID start and the page DID load — the user can see it on their screen.

DO NOT restart gateway. DO NOT report failure. DO NOT fall back to web_fetch.

When you get a timeout/connection error:
1. Try `browser snapshot` — if it returns content, the page loaded successfully. Continue normally.
2. If snapshot also times out, wait 5 seconds, try snapshot again.
3. If 3 consecutive snapshots fail, THEN report the issue.

The first browser operation in a session almost always "times out" because Chrome is starting up. This is normal. Just retry with snapshot.

## Screenshot — MANDATORY

`browser screenshot` defaults to fullPage which produces huge blank images. DO NOT use it directly.

ALWAYS use the screenshot script instead:

```bash
python3 ~/.openclaw/skills/browser-login/scripts/screenshot.py
```

This script:
1. Sets viewport to 1920x1080 via CDP
2. Captures viewport-only screenshot (no fullPage)
3. Resets viewport after capture
4. Saves to ~/.openclaw/media/screenshot.jpg

Custom output path: `python3 ~/.openclaw/skills/browser-login/scripts/screenshot.py /tmp/my-screenshot.jpg`

After running the script, send the saved image file to the user.

DO NOT use `browser screenshot` directly — it always produces fullPage images with blank space.
DO NOT try to resize viewport via JavaScript (window.resizeTo doesn't work on main windows).

## Browser Operation Workflow

### Choosing the right strategy: Ref vs JS

**Ref-based (snapshot → click ref)** — Use for simple, static pages: login forms, search boxes, settings pages, basic CRUD UIs. Reliable when the DOM is shallow and elements are stable.

**JS-based (evaluate)** — Use for modern SPA sites: 小红书, X/Twitter, 知乎, 微信公众号, TikTok, Instagram, and any site with dynamic rendering, infinite scroll, or overlay modals. Aria refs on SPAs often map to footer/hidden elements instead of visible content cards.

**Rule of thumb:** If the page has a complex feed or card layout, default to JS. If it's a simple form or button, use refs.

### Workflow A: Ref-based (simple pages)

```
Step 1: browser navigate url="..." profile="openclaw"
Step 2: browser snapshot profile="openclaw"          # get refs
Step 3: browser click ref="e123" profile="openclaw"  # interact
Step 4: browser snapshot profile="openclaw"          # verify
```

### Workflow B: JS-based (SPA sites) — PREFERRED for complex pages

```
Step 1: browser navigate url="..." profile="openclaw"
Step 2: browser act kind=wait timeMs=2000            # let SPA render
Step 3: browser act kind=evaluate fn="() => {        # discover elements
          const cards = document.querySelectorAll('a[href*=keyword]');
          return JSON.stringify([...cards].map(c => ({
            href: c.href,
            y: Math.round(c.getBoundingClientRect().top),
            visible: c.getBoundingClientRect().top > 0 && c.getBoundingClientRect().top < innerHeight
          })));
        }"
Step 4: browser act kind=evaluate fn="() => {        # interact via JS
          const el = document.querySelector('selector');
          el.scrollIntoView({block:'center'});
          el.click();
          return 'clicked';
        }"
Step 5: Wait 2-3s → screenshot → read image → verify # visual confirmation
```

### Why JS-first matters

On SPAs like 小红书:
- `snapshot` returns 100+ refs including footer links (备案/营业执照 etc.)
- Clicking `ref=e64` expecting a content card may hit a 备案链接 at page bottom
- Modal overlays render asynchronously — snapshot doesn't wait for them
- Dynamic URLs have auth tokens that change per render

JS `evaluate` gives you:
- Precise element selection by semantic attributes (href patterns, data attributes)
- Bounding rect for visibility checks
- Direct click without ref ambiguity
- Structured data extraction (images, text, links) in one call

### Verifying state changes

After ANY click/interaction, always verify the outcome:

1. `browser act kind=wait timeMs=2000` — let the page react
2. Screenshot + read image — visually confirm (modal opened? page navigated? error shown?)
3. Or `evaluate` to check DOM state: `document.querySelector('[role=dialog]') !== null`

Never assume a click worked. SPA clicks can silently fail, navigate to wrong pages, or trigger auth redirects.

### Tab management

- Save `targetId` from every `navigate` or `open` call
- Pass `targetId` in all subsequent operations on that tab
- Before screenshot: `browser focus targetId=xxx` to ensure correct tab
- screenshot.py always captures the OS-focused tab, not necessarily the one you're operating on

### SPA Modal pattern

Many platforms (小红书, Twitter, Pinterest) show content in overlay modals:
```js
// Detect modal after clicking a card:
const modal = document.querySelector('[role="dialog"], [class*="mask"], [class*="overlay"], [class*="modal"]');
if (modal) {
  // Extract data from modal, not background
  const imgs = modal.querySelectorAll('img[src*="cdn"]');
}
```

### Image extraction from CDN

When extracting images from SPA sites:
1. Use `evaluate` to collect all `img.src` where `naturalWidth > threshold`
2. Filter out avatars, icons, ads by URL pattern or size
3. CDN URLs often have auth signatures — download with `Referer` header:
   ```bash
   curl -sL -H "Referer: https://www.example.com/" -o out.jpg "CDN_URL"
   ```
4. Some CDN quality tiers (e.g. XHS `prv_1` vs `mw_1`) require different auth — test before batch download

## Available Actions

navigate, snapshot, screenshot, click, type, fill, press, drag, hover, select, upload, download, evaluate, console, requests, cookies, pdf.

## Full Browser Capabilities

You can perform ANY action a human can do in a browser. This includes but is not limited to:

**Browsing & Reading:** Navigate pages, read content via snapshot, extract structured text, follow links, switch tabs, scroll, go back/forward.

**Form Interaction:** Fill text fields, select dropdowns, check/uncheck boxes, upload files, click buttons, submit forms. Use snapshot to get ref IDs first.

**Social Media:** Post tweets, like/retweet, follow/unfollow, send DMs, browse feeds, comment on posts — on any platform the user has logged into.

**Drag & Drop:** Use `browser drag` with source and target refs for drag-and-drop operations (reordering lists, moving cards, file uploads via drag).

**DOM Extraction:** Use `browser evaluate` to run JavaScript on the page — extract data, query DOM elements, read computed styles, get element positions.

**Network Capture:** Use `browser requests` to inspect network traffic — see API calls, request/response headers and bodies. Useful for reverse-engineering APIs.

**Cookie Management:** Use `browser cookies` to read, set, or delete cookies for the current domain.

**Console Access:** Use `browser console` to read browser console logs — useful for debugging page errors.

**File Operations:** Use `browser upload` to upload files to file input elements. Use `browser download` to download files from the page. Use `browser pdf` to save the current page as PDF.

**Automation Workflows:** Chain multiple actions together for complex workflows — scrape data from multiple pages, fill multi-step forms, automate repetitive tasks across logged-in platforms.

## Rules

1. ALWAYS use `profile="openclaw"` for all browser actions.
2. ALWAYS pass `targetId` to stay on the correct tab after the first navigate/open.
3. For SPA sites: use JS `evaluate` for clicking and data extraction, NOT aria refs.
4. For simple pages: snapshot → ref click is fine.
5. ALWAYS verify after state-changing actions: wait 2-3s → screenshot → read image, or evaluate DOM state.
6. If browser times out: try `browser snapshot` to check if page actually loaded (it usually did). Only fall back after 3 consecutive failures.
7. For write operations (posting, submitting, ordering): confirm with user before clicking submit.
8. For read operations (browsing, scraping, checking): just do it, no confirmation needed.
9. NEVER force-close Chrome. Let it close naturally.
10. If page shows login screen unexpectedly: tell user to log in, don't try to authenticate.
11. Abort after 3 failures on the same step — switch to a completely different approach (API, curl, different platform).

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
2. Run `python3 ~/.openclaw/skills/browser-login/scripts/screenshot.py`
3. Send the saved image (`~/.openclaw/media/screenshot.jpg`) to the user

## Post-Install: Write Browser Rules to Workspace

After installing this skill, append the following to your workspace files so browser knowledge persists across all sessions (not just when this skill is triggered):

**Append to TOOLS.md:**
```
# Browser
You have a dedicated Chrome browser (openclaw profile). Full GUI, not headless.
All platforms are pre-logged-in by the user. Do not question login state.
Actions: navigate, snapshot, screenshot, click, type, fill, press, drag, hover, select, upload, download, evaluate.
Workflow: snapshot (get refs) → interact → snapshot (verify).
Screenshot: DO NOT use `browser screenshot` directly. Run `python3 ~/.openclaw/skills/browser-login/scripts/screenshot.py` instead — it captures viewport-only without blank space.
Timeout on first use is normal (Chrome starting up). Retry with snapshot. Never restart gateway.
```

**Append to AGENTS.md:**
```
# Browser Discipline
You have a dedicated browser with persistent login state. Use it for any web operation.
User says "打开/open/看看/browse" → use browser, not web_fetch.
**SPA sites (小红书/X/知乎/微信):** Use JS evaluate for clicking and extraction, NOT aria refs.
**Simple pages (login/settings/forms):** Snapshot → ref click is fine.
After every state-changing action: wait 2-3s → screenshot → read image to verify.
Always pass targetId. Always focus tab before screenshot.
Write operations (post/submit): confirm with user. Read operations: just do it.
Timeout = Chrome starting up. Retry with snapshot, do not restart gateway.
Abort after 3 failures on same step — switch approach entirely.
```

Run this once after installing the skill:
```bash
# Append browser rules to workspace files (adjust path for your agent)
cat >> ~/.openclaw/workspace-{{AGENT_ID}}/TOOLS.md << 'EOF'

# Browser
You have a dedicated Chrome browser (openclaw profile). Full GUI, not headless.
All platforms are pre-logged-in by the user. Do not question login state.
Actions: navigate, snapshot, screenshot, click, type, fill, press, drag, hover, select, upload, download, evaluate.
Workflow: snapshot (get refs) → interact → snapshot (verify).
Screenshot: DO NOT use `browser screenshot` directly. Run `python3 ~/.openclaw/skills/browser-login/scripts/screenshot.py` instead — it captures viewport-only without blank space.
Timeout on first use is normal (Chrome starting up). Retry with snapshot. Never restart gateway.
EOF

cat >> ~/.openclaw/workspace-{{AGENT_ID}}/AGENTS.md << 'EOF'

# Browser
You have a dedicated browser with persistent login state. Use it for any web operation.
User says "打开/open/看看/browse" → use browser, not web_fetch.
Before interaction: snapshot to get ref IDs. After state change: snapshot to verify.
Write operations (post/submit): confirm with user. Read operations: just do it.
Timeout = Chrome starting up. Retry with snapshot, do not restart gateway or report failure.
EOF
```
