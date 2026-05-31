"""
番茄小说热榜 - MCP Server
UUMit 数据广场 · 数据接口

提供番茄小说全平台榜单数据
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
    from .scraper import FanqieNovelScraper
except ImportError:
    from scraper import FanqieNovelScraper

server = Server("fanqie-novel-ranking")
scraper = FanqieNovelScraper()


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_fanqie_ranking",
            description="获取番茄小说排行榜。支持热读榜、新书榜、完本榜、推荐榜、飙升榜等多种榜单类型。",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "榜单类型: hot(热读榜), new_book(新书榜), finish(完本榜), recommend(推荐榜), rising(飙升榜)",
                        "enum": ["hot", "new_book", "finish", "recommend", "rising"],
                        "default": "hot",
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
            name="get_fanqie_novel_detail",
            description="获取指定番茄小说的详细信息，包括作者、热度、简介、字数、状态等",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "小说标题",
                    },
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="search_fanqie_novel",
            description="在番茄小说全站搜索指定关键词，返回匹配的小说列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词（书名或作者名）",
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="get_all_rankings_summary",
            description="获取番茄小说所有榜单的概览摘要，包含各榜单 TOP10 书名与热度",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_fanqie_ranking":
        category = arguments.get("category", "hot")
        size = arguments.get("size", 50)
        data = await scraper.get_ranking_list(category=category, size=size)
        return [TextContent(
            type="text",
            text=json.dumps(data, ensure_ascii=False, indent=2),
        )]

    elif name == "get_fanqie_novel_detail":
        title = arguments.get("title", "")
        data = await scraper.get_novel_detail(title=title)
        return [TextContent(
            type="text",
            text=json.dumps(data, ensure_ascii=False, indent=2),
        )]

    elif name == "search_fanqie_novel":
        keyword = arguments.get("keyword", "")
        data = await scraper.search_novel(keyword=keyword)
        return [TextContent(
            type="text",
            text=json.dumps(data, ensure_ascii=False, indent=2),
        )]

    elif name == "get_all_rankings_summary":
        categories = ["hot", "new_book", "finish", "recommend", "rising"]
        results = {}
        for cat in categories:
            data = await scraper.get_ranking_list(category=cat, size=10)
            results[cat] = {
                "category_name": data.get("category", cat),
                "top_10": [
                    {"rank": item["rank"], "title": item["title"], "hot_score": item["hot_score"]}
                    for item in data.get("items", [])[:10]
                ],
            }

        from datetime import datetime

        return [TextContent(
            type="text",
            text=json.dumps({
                "platform": "番茄小说",
                "update_time": datetime.now().isoformat(),
                "rankings_summary": results,
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
