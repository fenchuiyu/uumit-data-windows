"""
快手实时热搜榜单 - MCP Server
UUMit 数据广场 · 数据接口

启动方式:
    python server.py
    或
    mcp run server.py
"""

import json
import asyncio
import sys
import os

# 支持直接运行 (python server.py) 和被其他模块导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

try:
    from .scraper import KuaishouHotSearchScraper
except ImportError:
    from scraper import KuaishouHotSearchScraper

# 创建 MCP Server 实例
server = Server("kuaishou-hot-search")
scraper = KuaishouHotSearchScraper()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出该数据窗口提供的所有工具"""
    return [
        Tool(
            name="get_kuaishou_hot_search",
            description="获取快手实时热搜榜单，包含热搜排名、热度指数、趋势变化等信息。数据每30秒自动刷新。",
            inputSchema={
                "type": "object",
                "properties": {
                    "size": {
                        "type": "integer",
                        "description": "返回热搜条数，默认50，最大50",
                        "default": 50,
                        "minimum": 1,
                        "maximum": 50,
                    },
                },
            },
        ),
        Tool(
            name="search_kuaishou_topic",
            description="在快手热搜中搜索指定关键词，返回相关话题的热度与排名",
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
            name="get_kuaishou_trending_detail",
            description="获取指定快手热搜话题的详细信息，包括热度趋势、关联视频数等",
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
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理工具调用"""

    if name == "get_kuaishou_hot_search":
        size = arguments.get("size", 50)
        data = await scraper.get_hot_search_list(size=size)
        return [TextContent(
            type="text",
            text=json.dumps(data, ensure_ascii=False, indent=2),
        )]

    elif name == "search_kuaishou_topic":
        keyword = arguments.get("keyword", "")
        all_data = await scraper.get_hot_search_list(size=50)
        items = all_data.get("items", [])

        matched = [
            item for item in items
            if keyword.lower() in item.get("title", "").lower()
        ]

        result = {
            "keyword": keyword,
            "matched_count": len(matched),
            "items": matched,
        }
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2),
        )]

    elif name == "get_kuaishou_trending_detail":
        topic_title = arguments.get("topic_title", "")
        all_data = await scraper.get_hot_search_list(size=50)
        items = all_data.get("items", [])

        detail = None
        for item in items:
            if item.get("title") == topic_title:
                detail = {
                    **item,
                    "platform": "快手",
                    "data_source": "快手实时热搜榜",
                    "refresh_interval_seconds": 30,
                    "related_trends": [
                        {"title": t["title"], "rank": t["rank"]}
                        for t in items[:5] if t["title"] != topic_title
                    ],
                }
                break

        if not detail:
            detail = {"error": f"未找到话题: {topic_title}", "available_topics": [i["title"] for i in items[:10]]}

        return [TextContent(
            type="text",
            text=json.dumps(detail, ensure_ascii=False, indent=2),
        )]

    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"未知工具: {name}"}, ensure_ascii=False),
        )]


async def main():
    """启动 MCP Server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
