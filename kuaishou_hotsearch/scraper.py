"""
快手实时热搜榜单 - 数据抓取模块

数据来源: 快手公开热搜接口
提供实时热搜榜单、话题热度、排名变化等数据
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from typing import Optional
from common.base_scraper import BaseScraper


class KuaishouHotSearchScraper(BaseScraper):
    """快手实时热搜榜单抓取器"""

    # 快手热搜公开 API 端点
    HOT_SEARCH_API = "https://www.kuaishou.com/graphql"

    def __init__(self):
        super().__init__(cache_ttl=15)  # 15秒缓存，更快刷新

    async def get_hot_search_list(self, size: int = 50) -> dict:
        """
        获取快手实时热搜榜单

        Args:
            size: 返回热搜条数，默认50条

        Returns:
            {
                "platform": "快手",
                "update_time": "2026-05-31T17:30:00",
                "total": 50,
                "items": [
                    {
                        "rank": 1,
                        "title": "热搜标题",
                        "hot_score": 9854321,
                        "hot_tag": "热",
                        "trend": "up",         # up/down/stable/new
                        "cover_url": "https://...",
                        "description": "话题简介"
                    },
                    ...
                ]
            }
        """
        # 演示模式：跳过外部请求，毫秒级响应
        if self.demo_mode:
            return self._get_demo_data(size)
        try:
            # 方法1: 通过快手移动端热搜 API
            data = await self._fetch_via_mobile_api(size)
            return data
        except Exception:
            # 方法2: 通过网页端热搜接口
            return await self._fetch_via_web_api(size)

    async def _fetch_via_mobile_api(self, size: int) -> dict:
        """通过快手移动端 GraphQL API 获取热搜"""
        query = """
        query HotSearchQuery($count: Int!) {
            hotSearchList(count: $count) {
                rank
                title
                score
                hotTag
                trend
                coverUrl
                description
                videoCount
            }
        }
        """
        payload = {
            "operationName": "HotSearchQuery",
            "variables": {"count": size},
            "query": query,
        }
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://www.kuaishou.com",
        }

        resp = await self.post_json(self.HOT_SEARCH_API, payload, headers=headers)
        items = resp.get("data", {}).get("hotSearchList", [])
        return self._format_response(items)

    async def _fetch_via_web_api(self, size: int) -> dict:
        """通过快手网页端热搜接口获取（备用方案）"""
        try:
            html = await self.fetch_html(
                "https://www.kuaishou.com/",
                headers={"Referer": "https://www.kuaishou.com/"},
            )
        except Exception:
            return self._get_demo_data(size)

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        items = []

        # 解析热搜列表（快手页面结构可能变化，此处为通用解析逻辑）
        hot_items = soup.select('[class*="hot-search"] li, [class*="trending"] li, .search-rank-item')
        if not hot_items:
            # 尝试从 script 标签中的 JSON 数据提取
            import re
            import json
            scripts = soup.find_all("script")
            for script in scripts:
                if script.string and "hotSearchList" in script.string:
                    match = re.search(r'hotSearchList["\']?\s*:\s*(\[.*?\])', script.string, re.DOTALL)
                    if match:
                        try:
                            raw_data = json.loads(match.group(1))
                            items = raw_data
                        except json.JSONDecodeError:
                            pass
                    break

        if not items:
            return self._get_demo_data(size)

        return self._format_response(items)

    def _format_response(self, raw_items: list) -> dict:
        """格式化响应数据为统一结构"""
        from datetime import datetime

        items = []
        for i, item in enumerate(raw_items[:50]):
            if isinstance(item, dict):
                items.append({
                    "rank": item.get("rank", i + 1),
                    "title": item.get("title", item.get("name", "")),
                    "hot_score": item.get("score", item.get("hotScore", item.get("hot_score", 0))),
                    "hot_tag": item.get("hotTag", item.get("hot_tag", "")),
                    "trend": item.get("trend", "stable"),
                    "cover_url": item.get("coverUrl", item.get("cover_url", "")),
                    "description": item.get("description", item.get("desc", "")),
                })
            else:
                items.append({
                    "rank": i + 1,
                    "title": str(item),
                    "hot_score": 0,
                    "hot_tag": "",
                    "trend": "stable",
                    "cover_url": "",
                    "description": "",
                })

        return {
            "platform": "快手",
            "update_time": datetime.now().isoformat(),
            "total": len(items),
            "items": items,
        }

    def _get_demo_data(self, size: int = 50) -> dict:
        """返回演示数据（实际部署时请配置真实 API 密钥或 Cookie）"""
        from datetime import datetime

        demo_topics = [
            ("高考倒计时", 9854321, "爆", "up"),
            ("新说唱2026总决赛", 8765432, "热", "up"),
            ("北京中轴线申遗成功两周年", 7654321, "热", "stable"),
            ("量子计算机商用突破", 6543210, "新", "new"),
            ("端午节放假安排", 5432109, "热", "up"),
            ("世界女排联赛中国VS日本", 5321098, "热", "up"),
            ("AI绘画作品展火爆", 5210987, "热", "stable"),
            ("特斯拉FSD入华", 5109876, "新", "new"),
            ("《黑神话：悟空》DLC预告", 5098765, "热", "up"),
            ("南方多地暴雨预警", 4987654, "热", "stable"),
            ("中国芯片技术突破", 4876543, "新", "new"),
            ("NBA总决赛G4", 4765432, "热", "up"),
            ("年轻人为何爱上寺庙游", 4654321, "热", "stable"),
            ("高考加油", 4543210, "爆", "up"),
            ("清华发布AGI最新研究", 4432109, "新", "new"),
            ("周末去哪儿", 4321098, "热", "stable"),
            ("新能源汽车降价潮", 4210987, "热", "up"),
            ("航天员太空授课", 4109876, "热", "stable"),
            ("三伏天养生攻略", 4098765, "新", "new"),
            ("法网公开赛中国选手晋级", 3987654, "热", "up"),
        ]

        items = []
        for i, (title, score, tag, trend) in enumerate(demo_topics[:size]):
            items.append({
                "rank": i + 1,
                "title": title,
                "hot_score": score,
                "hot_tag": tag,
                "trend": trend,
                "cover_url": "",
                "description": f"#{title}# 正在快手热榜",
            })

        return {
            "platform": "快手",
            "update_time": datetime.now().isoformat(),
            "total": len(items),
            "items": items,
            "_note": "当前为演示数据，请参考 README 配置真实数据源",
        }
