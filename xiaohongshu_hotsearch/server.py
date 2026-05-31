"""
小红书热搜榜单 - MCP Server
UUMit 数据广场 · 数据接口

提供小红书全站及分类热搜数据
启动方式: python server.py
"""

import json
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

try:
    from .scraper import XiaohongshuHotSearchScraper
except ImportError:
    from scraper import XiaohongshuHotSearchScraper

server = Server("xiaohongshu-hot-search")
scraper = XiaohongshuHotSearchScraper()


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_xiaohongshu_hot_search",
            description="获取小红书实时热搜榜单。支持全站热搜及美妆、穿搭、美食、旅行、家居、健身、科技等分类热搜。",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "热搜分类: all(全站), beauty(美妆), fashion(穿搭), food(美食), travel(旅行), home(家居), fitness(健身), tech(科技)",
                        "enum": ["all", "beauty", "fashion", "food", "travel", "home", "fitness", "tech"],
                        "default": "all",
                    },
                    "size": {
                        "type": "integer",
                        "description": "返回条数，默认50，最大50",
                        "default": 50,
                        "minimum": 1,
                        "maximum": 50,
                    },
                },
            },
        ),
        Tool(
            name="get_xiaohongshu_topic_detail",
            description="获取小红书指定热搜话题的详细信息，包括排名趋势、关联话题等",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic_title": {
                        "type": "string",
                        "description": "热搜话题标题",
                    },
                },
                "required": ["topic_title"],
            },
        ),
        Tool(
            name="search_xiaohongshu_topic",
            description="在小红书热搜中搜索指定关键词，返回相关话题列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词",
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="get_category_summary",
            description="获取小红书各分类热搜概览，返回每个分类的 TOP5 话题",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_xiaohongshu_hot_search":
        category = arguments.get("category", "all")
        size = arguments.get("size", 50)
        data = await scraper.get_hot_search_list(category=category, size=size)
        return [TextContent(
            type="text",
            text=json.dumps(data, ensure_ascii=False, indent=2),
        )]

    elif name == "get_xiaohongshu_topic_detail":
        topic_title = arguments.get("topic_title", "")
        data = await scraper.get_topic_detail(topic_title=topic_title)
        return [TextContent(
            type="text",
            text=json.dumps(data, ensure_ascii=False, indent=2),
        )]

    elif name == "search_xiaohongshu_topic":
        keyword = arguments.get("keyword", "")
        data = await scraper.search_topic(keyword=keyword)
        return [TextContent(
            type="text",
            text=json.dumps(data, ensure_ascii=False, indent=2),
        )]

    elif name == "get_category_summary":
        categories = ["all", "beauty", "fashion", "food", "travel", "home", "fitness", "tech"]
        results = {}
        for cat in categories:
            data = await scraper.get_hot_search_list(category=cat, size=5)
            results[cat] = {
                "top_5": [
                    {"rank": item["rank"], "title": item["title"], "hot_score": item["hot_score"]}
                    for item in data.get("items", [])[:5]
                ],
            }

        # 获取全站数据中的分类名映射
        all_data = await scraper.get_hot_search_list(category="all", size=1)

        return [TextContent(
            type="text",
            text=json.dumps({
                "platform": "小红书",
                "update_time": all_data.get("update_time", ""),
                "category_summary": results,
            }, ensure_ascii=False, indent=2),
        )]

    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"未知工具: {name}"}, ensure_ascii=False),
        )]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
