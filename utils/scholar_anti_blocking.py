from urllib.parse import urlparse
import os
import time
import random
import threading
import logging
from typing import Optional, Dict, List

import requests

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENTS = [
    # A small rotating list. Users should expand this list responsibly.
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
]

def _env_bool(key: str, default: bool) -> bool:
    v = os.getenv(key)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")


class ScholarRequester:
    """A polite requester wrapper for making requests to Google Scholar with
    built-in delays, jitter, rotating user agents, optional proxy rotation,
    and exponential backoff on transient errors.

    This is NOT a guaranteed way to avoid blocks; it reduces request patterns
    that trigger automated blocking. Use responsibly and respect site terms.
    """

    def __init__(self,
                 min_delay: float = None,
                 max_delay: float = None,
                 max_retries: int = None,
                 backoff_factor: float = None,
                 rotate_user_agents: Optional[bool] = None,
                 user_agents: Optional[List[str]] = None,
                 proxy_list: Optional[List[str]] = None):

        self.min_delay = float(min_delay if min_delay is not None else os.getenv('SCHOLAR_MIN_DELAY', 3))
        self.max_delay = float(max_delay if max_delay is not None else os.getenv('SCHOLAR_MAX_DELAY', 8))
        if self.max_delay < self.min_delay:
            self.max_delay = self.min_delay

        self.max_retries = int(max_retries if max_retries is not None else os.getenv('SCHOLAR_MAX_RETRIES', 5))
        self.backoff_factor = float(backoff_factor if backoff_factor is not None else os.getenv('SCHOLAR_BACKOFF_FACTOR', 2.0))

        self.rotate_user_agents = bool(rotate_user_agents if rotate_user_agents is not None else _env_bool('SCHOLAR_ROTATE_USER_AGENTS', True))
        self.user_agents = user_agents or os.getenv('SCHOLAR_USER_AGENTS')
        if isinstance(self.user_agents, str):
            # allow comma separated env var
            self.user_agents = [u.strip() for u in self.user_agents.split(',') if u.strip()]

        if not self.user_agents:
            self.user_agents = DEFAULT_USER_AGENTS.copy()

        proxy_env = os.getenv('SCHOLAR_PROXY_LIST')
        if proxy_env:
            self.proxy_list = [p.strip() for p in proxy_env.split(',') if p.strip()]
        else:
            self.proxy_list = proxy_list or []

        self.session = requests.Session()
        # Keep a small map of last request timestamps per host to enforce per-host delays
        self._last_request_time: Dict[str, float] = {}
        self._locks: Dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()

    def _get_lock_for_host(self, host: str) -> threading.Lock:
        with self._global_lock:
            if host not in self._locks:
                self._locks[host] = threading.Lock()
            return self._locks[host]

    def _select_user_agent(self) -> str:
        if not self.user_agents:
            return DEFAULT_USER_AGENTS[0]
        if self.rotate_user_agents:
            return random.choice(self.user_agents)
        return self.user_agents[0]

    def _select_proxy(self) -> Optional[Dict[str,str]]:
        if not self.proxy_list:
            return None
        proxy = random.choice(self.proxy_list)
        # Expect proxies in the form http://host:port or https://host:port
        return {"http": proxy, "https": proxy}

    def _sleep_for_rate_limit(self, host: str):
        lock = self._get_lock_for_host(host)
        with lock:
            now = time.time()
            last = self._last_request_time.get(host)
            if last is None:
                # first request to this host
                self._last_request_time[host] = now
                return
            # compute a polite delay with jitter
            delay = random.uniform(self.min_delay, self.max_delay)
            earliest = last + delay
            if earliest > now:
                to_wait = earliest - now
                logger.debug("Sleeping %.2fs before requesting %s (polite delay)", to_wait, host)
                time.sleep(to_wait)
            self._last_request_time[host] = time.time()

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        parsed = urlparse(url)
        host = parsed.netloc
        attempt = 0

        # Set headers if not provided
        headers = kwargs.pop('headers', {}) or {}
        if 'User-Agent' not in {k.title(): v for k, v in headers.items()}:
            headers.setdefault('User-Agent', self._select_user_agent())
        # sensible defaults
        headers.setdefault('Accept-Language', 'en-US,en;q=0.9')
        headers.setdefault('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        headers.setdefault('Connection', 'keep-alive')
        kwargs['headers'] = headers

        while True:
            attempt += 1
            # enforce per-host polite delay
            self._sleep_for_rate_limit(host)

            # select proxy if configured
            proxies = kwargs.get('proxies')
            if not proxies and self.proxy_list:
                proxies = self._select_proxy()
                if proxies:
                    kwargs['proxies'] = proxies

            try:
                logger.debug("Requesting %s %s (attempt %d)", method, url, attempt)
                resp = self.session.request(method, url, **kwargs)
            except requests.RequestException as e:
                logger.warning("Network error on attempt %d for %s: %s", attempt, url, e)
                if attempt >= self.max_retries:
                    raise
                sleep_for = (self.backoff_factor ** attempt) + random.uniform(0, 1)
                logger.debug("Sleeping %.2fs after exception before retry", sleep_for)
                time.sleep(sleep_for)
                continue

            # If Scholar returns common throttling/anti-bot status codes, backoff and retry
            if resp.status_code in (429, 503, 403):
                # 403 might be issued by Google for blocks; treat it carefully
                logger.warning("Status %s for %s (attempt %d). Backing off.", resp.status_code, url, attempt)
                if attempt >= self.max_retries:
                    return resp
                sleep_for = (self.backoff_factor ** attempt) + random.uniform(self.min_delay, self.max_delay)
                logger.debug("Sleeping %.2fs before retry", sleep_for)
                time.sleep(sleep_for)
                continue

            # successful or other non-retryable status
            return resp


# Convenience helper
_default_requester: Optional[ScholarRequester] = None

def get_default_requester() -> ScholarRequester:
    global _default_requester
    if _default_requester is None:
        _default_requester = ScholarRequester()
    return _default_requester


def scholar_get(url: str, **kwargs) -> requests.Response:
    """Simple functional wrapper for GET requests using the default requester."""
    return get_default_requester().request('GET', url, **kwargs)