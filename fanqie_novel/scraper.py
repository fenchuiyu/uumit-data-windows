"""
番茄小说热榜 - 数据抓取模块

数据来源: 番茄小说公开 API 与网页榜单
提供热门榜单、分类排行、小说详情等数据

番茄小说是字节跳动旗下的免费阅读平台 (fanqienovel.com)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from typing import Optional
from common.base_scraper import BaseScraper


class FanqieNovelScraper(BaseScraper):
    """番茄小说热榜抓取器"""

    # 番茄小说 API 基础地址
    BASE_API = "https://fanqienovel.com"
    RANKING_API = "https://fanqienovel.com/api/ranking"

    def __init__(self):
        super().__init__(cache_ttl=60)  # 1分钟缓存

    async def get_ranking_list(self, category: str = "hot", size: int = 50) -> dict:
        """
        获取番茄小说排行榜

        Args:
            category: 榜单类型
                - hot: 热读榜
                - new_book: 新书榜
                - finish: 完本榜
                - recommend: 推荐榜
                - rising: 飙升榜
            size: 返回条数

        Returns:
            {
                "platform": "番茄小说",
                "category": "热读榜",
                "update_time": "2026-05-31T17:30:00",
                "total": 50,
                "items": [...]
            }
        """
        # 演示模式：跳过外部请求，毫秒级响应
        if self.demo_mode:
            data = self._get_demo_data(category, size)
            cat_names = {"hot": "热读榜", "new_book": "新书榜", "finish": "完本榜", "recommend": "推荐榜", "rising": "飙升榜"}
            data["category"] = cat_names.get(category, category)
            return data

        category_map = {
            "hot": "热读榜",
            "new_book": "新书榜",
            "finish": "完本榜",
            "recommend": "推荐榜",
            "rising": "飙升榜",
        }

        try:
            data = await self._fetch_ranking_via_api(category, size)
            data["category"] = category_map.get(category, category)
            return data
        except Exception:
            return await self._fetch_ranking_via_web(category, size)

    async def _fetch_ranking_via_api(self, category: str, size: int) -> dict:
        """通过 API 获取排行榜"""
        headers = {
            "Origin": self.BASE_API,
            "Referer": f"{self.BASE_API}/ranking",
        }
        params = {
            "category": category,
            "page_size": size,
            "page": 1,
        }

        resp = await self.fetch_json(self.RANKING_API, params=params, headers=headers)
        items = resp.get("data", {}).get("list", resp.get("data", []))
        return self._format_response(items, category)

    async def _fetch_ranking_via_web(self, category: str, size: int) -> dict:
        """通过网页解析获取排行榜（备用方案）"""
        try:
            url = f"{self.BASE_API}/ranking/{category}"
            html = await self.fetch_html(url, headers={"Referer": self.BASE_API})
        except Exception:
            return self._get_demo_data(category, size)

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        items = []

        # 尝试从页面内嵌 JSON 数据提取
        import re
        import json

        scripts = soup.find_all("script")
        for script in scripts:
            if script.string and "rankingList" in script.string:
                match = re.search(
                    r'(?:rankingList|rankList|__NEXT_DATA__)[^=]*[=:]\s*(\[.*?\]|\{.*?\})',
                    script.string,
                    re.DOTALL,
                )
                if match:
                    try:
                        raw = json.loads(match.group(1))
                        if isinstance(raw, list):
                            items = raw
                        elif isinstance(raw, dict):
                            items = raw.get("list", raw.get("items", raw.get("rankingList", [])))
                    except json.JSONDecodeError:
                        pass
                    break

        if not items:
            # 尝试 CSS 选择器解析
            book_items = soup.select(
                '[class*="book-item"], [class*="rank-item"], .ranking-list li, .book-card'
            )
            for item in book_items[:size]:
                title_el = item.select_one('[class*="title"], [class*="name"], h3, h4')
                author_el = item.select_one('[class*="author"], [class*="writer"]')
                score_el = item.select_one('[class*="score"], [class*="hot"]')
                cover_el = item.select_one("img")

                items.append({
                    "title": title_el.get_text(strip=True) if title_el else "",
                    "author": author_el.get_text(strip=True) if author_el else "",
                    "hot_score": score_el.get_text(strip=True) if score_el else "",
                    "cover_url": cover_el.get("src", "") if cover_el else "",
                })

        if not items:
            return self._get_demo_data(category, size)

        return self._format_response(items, category)

    def _format_response(self, raw_items: list, category: str) -> dict:
        """格式化响应数据"""
        items = []
        for i, item in enumerate(raw_items[:50]):
            if isinstance(item, dict):
                items.append({
                    "rank": item.get("rank", item.get("ranking", i + 1)),
                    "title": item.get("title", item.get("name", item.get("book_name", ""))),
                    "author": item.get("author", item.get("author_name", "")),
                    "hot_score": item.get("hot_score", item.get("score", item.get("heat", 0))),
                    "category": item.get("category", item.get("tag", "")),
                    "status": item.get("status", item.get("book_status", "连载中")),
                    "word_count": item.get("word_count", item.get("wordCount", 0)),
                    "cover_url": item.get("cover_url", item.get("cover", item.get("image", ""))),
                    "intro": item.get("intro", item.get("description", item.get("desc", ""))),
                    "trend": item.get("trend", "stable"),
                })
            else:
                items.append({
                    "rank": i + 1,
                    "title": str(item),
                    "author": "",
                    "hot_score": 0,
                    "category": "",
                    "status": "连载中",
                    "word_count": 0,
                    "cover_url": "",
                    "intro": "",
                    "trend": "stable",
                })

        return {
            "platform": "番茄小说",
            "update_time": datetime.now().isoformat(),
            "total": len(items),
            "items": items,
        }

    async def get_novel_detail(self, title: str = "") -> dict:
        """获取指定小说的详细信息"""
        all_data = await self.get_ranking_list(category="hot", size=50)
        items = all_data.get("items", [])

        for item in items:
            if title and item.get("title") == title:
                return {
                    **item,
                    "platform": "番茄小说",
                    "data_source": "番茄小说热榜",
                    "chapters": "2000+",
                    "reader_count": item.get("hot_score", 0) * 100,
                    "tags": ["免费", "热门", "推荐"],
                }

        return {"error": f"未找到小说: {title}", "available_novels": [i["title"] for i in items[:10]]}

    async def search_novel(self, keyword: str) -> dict:
        """搜索小说"""
        all_categories = ["hot", "new_book", "finish", "recommend", "rising"]
        all_results = []

        for cat in all_categories:
            data = await self.get_ranking_list(category=cat, size=50)
            items = data.get("items", [])
            matched = [
                item for item in items
                if keyword.lower() in item.get("title", "").lower()
                or keyword.lower() in item.get("author", "").lower()
            ]
            all_results.extend(matched)

        # 去重
        seen = set()
        unique_results = []
        for item in all_results:
            if item["title"] not in seen:
                seen.add(item["title"])
                unique_results.append(item)

        return {
            "keyword": keyword,
            "matched_count": len(unique_results),
            "items": unique_results[:20],
        }

    def _get_demo_data(self, category: str, size: int = 50) -> dict:
        """返回演示数据"""
        category_map = {
            "hot": "热读榜",
            "new_book": "新书榜",
            "finish": "完本榜",
            "recommend": "推荐榜",
            "rising": "飙升榜",
        }

        demo_books = [
            ("我在战国搞基建", "青衫仗剑", 9854321, "历史", "连载中", "穿越战国，从一砖一瓦开始改变世界"),
            ("重生之科技霸主", "墨香公子", 8765432, "都市", "连载中", "重回2000年，这一次他要打造科技帝国"),
            ("九霄帝尊", "天蚕土豆", 7654321, "玄幻", "连载中", "少年持剑，踏破九霄，成就无上帝尊"),
            ("王妃她不按套路来", "风铃草", 6543210, "古代言情", "连载中", "穿越成王妃，她决定躺平摆烂"),
            ("星際聯邦檢察官", "银河漫游者", 6432109, "科幻", "连载中", "在星际联邦中追寻真相与正义"),
            ("修仙从种田开始", "笔走龙蛇", 6321098, "仙侠", "连载中", "种田也能成仙？且看农家少年的修仙之路"),
            ("我的系统是废柴", "键盘侠客", 6210987, "游戏", "连载中", "绑定了一个废柴系统，却意外走上人生巅峰"),
            ("医妃倾城", "花间一壶酒", 6109876, "古代言情", "连载中", "一手医术，搅动朝堂风云"),
            ("修真聊天群", "圣骑士的传说", 6098765, "都市", "完本", "一个修真聊天群，改变了他的平凡人生"),
            ("大王饶命", "会说话的肘子", 5987654, "都市", "完本", "灵气复苏时代，靠怼人就能变强"),
            ("第一序列", "会说话的肘子", 5876543, "科幻", "完本", "废土之上，人类最后的希望"),
            ("诡秘之主", "爱潜水的乌贼", 5765432, "奇幻", "完本", "蒸汽朋克下的诡秘世界"),
            ("大奉打更人", "卖报小郎君", 5654321, "仙侠", "完本", "打更人许七安的奇幻冒险"),
            ("我的1979", "争斤论两花花帽", 5543210, "都市", "完本", "重回1979，抓住每一个时代的机遇"),
            ("夜的命名术", "会说话的肘子", 5432109, "都市", "连载中", "当黑夜降临，命名术将改变一切"),
            ("星辰变", "我吃西红柿", 5321098, "仙侠", "完本", "一颗流星，改变了他的命运"),
            ("全职高手", "蝴蝶蓝", 5210987, "游戏", "完本", "荣耀，从来不是一个人的游戏"),
            ("赘婿", "愤怒的香蕉", 5109876, "历史", "连载中", "一个现代人穿越成赘婿的故事"),
            ("雪中悍刀行", "烽火戏诸侯", 5098765, "武侠", "完本", "北凉世子徐凤年的江湖行"),
            ("剑来", "烽火戏诸侯", 4987654, "仙侠", "连载中", "陈平安的江湖之路"),
        ]

        items = []
        for i, (title, author, score, cat, status, intro) in enumerate(demo_books[:size]):
            items.append({
                "rank": i + 1,
                "title": title,
                "author": author,
                "hot_score": score,
                "category": cat,
                "status": status,
                "word_count": 1000000 + (i * 150000),
                "cover_url": "",
                "intro": intro,
                "trend": "up" if i < 5 else ("stable" if i < 10 else "down"),
            })

        return {
            "platform": "番茄小说",
            "category": category_map.get(category, category),
            "update_time": datetime.now().isoformat(),
            "total": len(items),
            "items": items,
            "_note": "当前为演示数据，请参考 README 配置真实数据源",
        }
