# Anti-blocking & polite requester for Google Scholar

This document describes the polite requester utility included at `utils/scholar_anti_blocking.py`, recommended configuration, and integration notes.

## What this utility provides
- Per-host rate limiting with jitter (min/max delay).
- Rotating User-Agent header (configurable).
- Optional proxy rotation (configurable via environment).
- Exponential backoff and retry on transient errors and common anti-bot status codes (429, 503, 403).
- Thread-safe per-host locking so concurrent workers behave politely.

This reduces the chance of being throttled by automated heuristics, but it does NOT guarantee avoidance of blocks. Always follow Google Scholar's terms of service and robots policy; prefer official APIs where available.

## Usage (example)
```python
from utils.scholar_anti_blocking import scholar_get, ScholarRequester

# Simple functional use (uses environment or defaults)
resp = scholar_get("https://scholar.google.com/scholar?q=quantum+computing")
html = resp.text

# Or create and configure a requester instance
r = ScholarRequester(min_delay=4, max_delay=10, max_retries=6,
                     backoff_factor=2.0, rotate_user_agents=True,
                     proxy_list=["http://10.0.0.1:3128"])
resp = r.request("GET", "https://scholar.google.com/scholar?q=ai")
```

## Recommended defaults
- SCHOLAR_MIN_DELAY: 3s
- SCHOLAR_MAX_DELAY: 8s
- SCHOLAR_MAX_RETRIES: 4-6
- Rotate user agents: enabled
- Proxy usage: only if you legally control the proxies and understand rate limits per IP.

## Operational notes & best practices
- Expand the USER-AGENT list to realistic, modern browser strings, but do not impersonate humans or misrepresent identity.
- Keep request volume low; prefer batching across longer time windows.
- Use per-host delays — this utility does that by default.
- Respect robots.txt and terms of service. If your use case is heavy or repeated, consider institutional access or APIs.
- Monitor responses: many blocks are signaled by 429/503/403. Log these and stop aggressive retries.
- For distributed scraping, stagger start times and randomize intervals to avoid synchronized bursts.

## Security & privacy
- Do not commit `.env` with secrets or proxy credentials. Use the provided `.env.example` as a template.
- If using proxies, ensure they are authorized and secure.

## Suggested repo changes
- Keep `utils/scholar_anti_blocking.py` at `utils/` (already added).
- Add `.env.example` (already pushed to `anti-blocking`).
- Add `ANTI_BLOCKING.md` to the repo root (this file).
- Optionally add a short note to README linking to `ANTI_BLOCKING.md`.