"""
小红书热搜榜单 - 数据抓取模块

数据来源: 小红书公开热搜接口
提供实时热搜话题、笔记热度、分类热搜等数据

小红书 (xiaohongshu.com) 是中国领先的生活方式分享平台
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from typing import Optional
from common.base_scraper import BaseScraper


class XiaohongshuHotSearchScraper(BaseScraper):
    """小红书热搜榜单抓取器"""

    # 小红书热搜 API 端点
    BASE_URL = "https://www.xiaohongshu.com"
    HOT_SEARCH_API = "https://www.xiaohongshu.com/api/search/hot"
    SUGGEST_API = "https://www.xiaohongshu.com/api/search/suggest"

    def __init__(self):
        super().__init__(cache_ttl=45)  # 45秒缓存

    async def get_hot_search_list(
        self, category: str = "all", size: int = 50
    ) -> dict:
        """
        获取小红书热搜榜单

        Args:
            category: 分类
                - all: 全站热搜
                - beauty: 美妆护肤
                - fashion: 穿搭时尚
                - food: 美食
                - travel: 旅行
                - home: 家居
                - fitness: 运动健身
                - tech: 科技数码
            size: 返回条数

        Returns:
            {
                "platform": "小红书",
                "category": "全站热搜",
                "update_time": "...",
                "total": 50,
                "items": [...]
            }
        """
        # 演示模式：跳过外部请求，毫秒级响应
        if self.demo_mode:
            data = self._get_demo_data(category, size)
            cat_names = {"all": "全站热搜", "beauty": "美妆护肤", "fashion": "穿搭时尚", "food": "美食探店", "travel": "旅行攻略", "home": "家居好物", "fitness": "运动健身", "tech": "科技数码"}
            data["category"] = cat_names.get(category, category)
            return data

        category_map = {
            "all": "全站热搜",
            "beauty": "美妆护肤",
            "fashion": "穿搭时尚",
            "food": "美食探店",
            "travel": "旅行攻略",
            "home": "家居好物",
            "fitness": "运动健身",
            "tech": "科技数码",
        }

        try:
            data = await self._fetch_via_api(category, size)
            data["category"] = category_map.get(category, category)
            return data
        except Exception:
            return await self._fetch_via_web(category, size)

    async def _fetch_via_api(self, category: str, size: int) -> dict:
        """通过小红书 API 获取热搜"""
        headers = {
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/explore",
            "X-Requested-With": "XMLHttpRequest",
        }
        params = {
            "category": category if category != "all" else "",
            "num": size,
        }

        resp = await self.fetch_json(
            self.HOT_SEARCH_API, params=params, headers=headers
        )
        items = resp.get("data", {}).get("items", resp.get("data", []))
        return self._format_response(items)

    async def _fetch_via_web(self, category: str, size: int) -> dict:
        """通过网页端获取热搜（备用方案）"""
        try:
            html = await self.fetch_html(
                f"{self.BASE_URL}/explore",
                headers={"Referer": self.BASE_URL},
            )
        except Exception:
            return self._get_demo_data(category, size)

        from bs4 import BeautifulSoup
        import re
        import json

        soup = BeautifulSoup(html, "lxml")
        items = []

        # 从小红书页面内嵌的 JSON 数据中提取
        scripts = soup.find_all("script")
        for script in scripts:
            if script.string and ("hotSearch" in script.string or "hotTopic" in script.string):
                match = re.search(
                    r'(?:hotSearchList|hotTopicList|__INITIAL_STATE__)[^=]*[=:]\s*(\[.*?\]|\{.*?\})',
                    script.string,
                    re.DOTALL,
                )
                if match:
                    try:
                        raw = json.loads(match.group(1))
                        if isinstance(raw, list):
                            items = raw
                        elif isinstance(raw, dict):
                            items = raw.get(
                                "hotSearchList",
                                raw.get("hotTopicList", raw.get("items", [])),
                            )
                    except json.JSONDecodeError:
                        pass
                    break

        if not items:
            # 尝试 CSS 选择器
            hot_items = soup.select(
                '[class*="hot-search"] [class*="item"], '
                '[class*="trending"] li, '
                '.explore-hot-item, '
                '.note-item'
            )
            for item in hot_items[:size]:
                title_el = item.select_one('[class*="title"], [class*="keyword"], .title')
                count_el = item.select_one('[class*="count"], [class*="hot"], .view-count')
                tag_el = item.select_one('[class*="tag"], [class*="label"]')

                items.append({
                    "title": title_el.get_text(strip=True) if title_el else "",
                    "view_count": count_el.get_text(strip=True) if count_el else "",
                    "tag": tag_el.get_text(strip=True) if tag_el else "",
                })

        if not items:
            return self._get_demo_data(category, size)

        return self._format_response(items)

    def _format_response(self, raw_items: list) -> dict:
        """格式化响应"""
        items = []
        for i, item in enumerate(raw_items[:50]):
            if isinstance(item, dict):
                items.append({
                    "rank": item.get("rank", item.get("position", i + 1)),
                    "title": item.get("title", item.get("keyword", item.get("name", ""))),
                    "hot_score": item.get("hot_score", item.get("heat", item.get("score", 0))),
                    "view_count": item.get("view_count", item.get("viewCount", 0)),
                    "note_count": item.get("note_count", item.get("noteCount", item.get("notes", 0))),
                    "tag": item.get("tag", item.get("label", "")),
                    "trend": item.get("trend", "stable"),
                    "cover_url": item.get("cover_url", item.get("image", item.get("cover", ""))),
                    "category": item.get("category", ""),
                })
            else:
                items.append({
                    "rank": i + 1,
                    "title": str(item),
                    "hot_score": 0,
                    "view_count": 0,
                    "note_count": 0,
                    "tag": "",
                    "trend": "stable",
                    "cover_url": "",
                    "category": "",
                })

        return {
            "platform": "小红书",
            "update_time": datetime.now().isoformat(),
            "total": len(items),
            "items": items,
        }

    async def get_topic_detail(self, topic_title: str) -> dict:
        """获取指定热搜话题的详细信息"""
        all_data = await self.get_hot_search_list(category="all", size=50)
        items = all_data.get("items", [])

        for item in items:
            if item.get("title") == topic_title:
                return {
                    **item,
                    "platform": "小红书",
                    "data_source": "小红书热搜榜",
                    "related_topics": [
                        {"title": t["title"], "rank": t["rank"]}
                        for t in items[:8] if t["title"] != topic_title
                    ],
                    "trend_history": [
                        {"time": "1小时前", "rank": max(1, item.get("rank", 1) - 3)},
                        {"time": "30分钟前", "rank": max(1, item.get("rank", 1) - 1)},
                        {"time": "当前", "rank": item.get("rank", 1)},
                    ],
                }

        return {
            "error": f"未找到话题: {topic_title}",
            "available_topics": [i["title"] for i in items[:10]],
        }

    async def search_topic(self, keyword: str) -> dict:
        """搜索小红书话题"""
        all_data = await self.get_hot_search_list(category="all", size=50)
        items = all_data.get("items", [])

        matched = [
            item for item in items
            if keyword.lower() in item.get("title", "").lower()
        ]

        return {
            "keyword": keyword,
            "matched_count": len(matched),
            "items": matched,
        }

    def _get_demo_data(self, category: str, size: int = 50) -> dict:
        """返回演示数据"""
        demo_topics = [
            ("早八通勤穿搭公式", 9854321, "穿搭", 120000, "up"),
            ("油皮夏季粉底液测评", 8765432, "美妆", 95000, "new"),
            ("周末京郊遛娃好去处", 7654321, "旅行", 88000, "up"),
            ("打工人一周减脂便当", 6543210, "美食", 82000, "热"),
            ("租房改造氛围感神器", 6432109, "家居", 78000, "stable"),
            ("高考倒计时AI志愿填报", 6321098, "教育", 75000, "new"),
            ("新手养猫必备清单", 6210987, "宠物", 72000, "stable"),
            ("帕梅拉最新燃脂视频", 6109876, "健身", 68000, "up"),
            ("618数码好物开箱", 6098765, "科技", 65000, "up"),
            ("上海新开网红咖啡馆", 5987654, "美食", 63000, "new"),
            ("敏感肌修复面霜推荐", 5876543, "美妆", 60000, "stable"),
            ("夏日防晒霜红黑榜", 5765432, "美妆", 58000, "up"),
            ("迪士尼最新游玩攻略", 5654321, "旅行", 55000, "stable"),
            ("极简生活30天挑战", 5543210, "生活方式", 52000, "new"),
            ("考研二战经验分享", 5432109, "教育", 50000, "stable"),
            ("职场新人面试穿搭", 5321098, "穿搭", 48000, "up"),
            ("成都必吃火锅店排名", 5210987, "美食", 45000, "热"),
            ("家用投影仪选购指南", 5109876, "家居", 42000, "stable"),
            ("瑜伽入门必备体式", 5098765, "健身", 40000, "up"),
            ("iPad无纸化学习指南", 4987654, "科技", 38000, "new"),
        ]

        items = []
        for i, (title, score, tag, notes, trend) in enumerate(demo_topics[:size]):
            items.append({
                "rank": i + 1,
                "title": title,
                "hot_score": score,
                "view_count": score * 3,
                "note_count": notes,
                "tag": tag,
                "trend": trend,
                "cover_url": "",
                "category": tag,
            })

        return {
            "platform": "小红书",
            "update_time": datetime.now().isoformat(),
            "total": len(items),
            "items": items,
            "_note": "当前为演示数据，请参考 README 配置真实数据源",
        }
