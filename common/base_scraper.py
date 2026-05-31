"""
UUMit 数据窗口 - 公共基础爬虫模块
提供 HTTP 请求封装、重试机制、User-Agent 轮换等通用功能
"""

import asyncio
import hashlib
import json
import os
import time
from typing import Optional, Any

import httpx
from fake_useragent import UserAgent


class BaseScraper:
    """数据抓取基类，封装通用的 HTTP 请求与缓存逻辑"""

    def __init__(self, cache_ttl: int = 60):
        """
        Args:
            cache_ttl: 缓存有效期（秒），默认60秒避免频繁请求
        """
        self.cache_ttl = cache_ttl
        self._cache: dict[str, tuple[float, Any]] = {}
        self.demo_mode = os.environ.get("DEMO_MODE", "1") == "1"  # 默认演示模式，秒回
        try:
            self._ua = UserAgent()
        except Exception:
            self._ua = None  # 降级使用静态 UA

    def _get_headers(self, referer: str = "") -> dict[str, str]:
        """生成随机请求头，模拟浏览器访问"""
        FALLBACK_UA = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
        ua = self._ua.random if self._ua else FALLBACK_UA
        return {
            "User-Agent": ua,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": referer or "https://www.google.com/",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

    def _cache_key(self, url: str, params: dict = None) -> str:
        raw = url + json.dumps(params or {}, sort_keys=True)
        return hashlib.md5(raw.encode()).hexdigest()

    def _get_cache(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry:
            ts, data = entry
            if time.time() - ts < self.cache_ttl:
                return data
            del self._cache[key]
        return None

    def _set_cache(self, key: str, data: Any) -> None:
        self._cache[key] = (time.time(), data)

    async def fetch_json(
        self,
        url: str,
        params: dict = None,
        headers: dict = None,
        use_cache: bool = True,
    ) -> dict:
        """GET 请求并返回 JSON"""
        cache_key = self._cache_key(url, params)
        if use_cache:
            cached = self._get_cache(cache_key)
            if cached is not None:
                return cached

        merged_headers = self._get_headers()
        if headers:
            merged_headers.update(headers)

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            for attempt in range(3):
                try:
                    resp = await client.get(url, params=params, headers=merged_headers)
                    resp.raise_for_status()
                    data = resp.json()
                    if use_cache:
                        self._set_cache(cache_key, data)
                    return data
                except Exception as e:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(1.0 * (attempt + 1))

    async def fetch_html(
        self,
        url: str,
        params: dict = None,
        headers: dict = None,
        use_cache: bool = True,
    ) -> str:
        """GET 请求并返回 HTML 文本"""
        cache_key = self._cache_key(url, params) + "_html"
        if use_cache:
            cached = self._get_cache(cache_key)
            if cached is not None:
                return cached

        merged_headers = self._get_headers()
        merged_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        if headers:
            merged_headers.update(headers)

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            for attempt in range(3):
                try:
                    resp = await client.get(url, params=params, headers=merged_headers)
                    resp.raise_for_status()
                    text = resp.text
                    if use_cache:
                        self._set_cache(cache_key, text)
                    return text
                except Exception as e:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(1.0 * (attempt + 1))

    async def post_json(
        self,
        url: str,
        json_data: dict = None,
        headers: dict = None,
    ) -> dict:
        """POST 请求并返回 JSON"""
        merged_headers = self._get_headers()
        merged_headers["Content-Type"] = "application/json"
        if headers:
            merged_headers.update(headers)

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            for attempt in range(3):
                try:
                    resp = await client.post(url, json=json_data, headers=merged_headers)
                    resp.raise_for_status()
                    return resp.json()
                except Exception as e:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(1.0 * (attempt + 1))
