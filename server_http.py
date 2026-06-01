"""
UUMit 数据广场 · REST API Server
================================
为 UUMit「创建接口 → 上游配置」提供 REST API 端点。

启动方式:
    python server_http.py
    默认监听 http://0.0.0.0:8000

三个数据窗口的 REST API:
    GET /api/kuaishou/list?size=50          → 快手实时热搜
    GET /api/kuaishou/search?keyword=xxx    → 快手话题搜索
    GET /api/kuaishou/detail?topic=xxx      → 快手话题详情

    GET /api/fanqie/list?category=hot&size=50 → 番茄小说排行榜
    GET /api/fanqie/search?keyword=xxx        → 番茄小说搜索
    GET /api/fanqie/detail?title=xxx          → 番茄小说详情
    GET /api/fanqie/summary                   → 番茄全榜概览

    GET /api/xiaohongshu/list?category=all&size=50 → 小红书热搜
    GET /api/xiaohongshu/search?keyword=xxx        → 小红书话题搜索
    GET /api/xiaohongshu/detail?topic=xxx          → 小红书话题详情
    GET /api/xiaohongshu/summary                   → 小红分类概览
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse

# ── 导入数据抓取器 ────────────────────────────────────────
from kuaishou_hotsearch.scraper import KuaishouHotSearchScraper
from fanqie_novel.scraper import FanqieNovelScraper
from xiaohongshu_hotsearch.scraper import XiaohongshuHotSearchScraper
from s71200_ref.instructions import get_all_categories, get_category, search_instructions, get_instruction_detail

ks = KuaishouHotSearchScraper()
fq = FanqieNovelScraper()
xhs = XiaohongshuHotSearchScraper()


# ── 通用 JSON 响应封装 ────────────────────────────────────
def json_response(data: dict, status: int = 200):
    return JSONResponse(data, status_code=status)


def error_response(msg: str, status: int = 400):
    return JSONResponse({"error": msg, "success": False}, status_code=status)


# ═══════════════════════════════════════════════════════════
#  快手实时热搜 REST API
# ═══════════════════════════════════════════════════════════

async def ks_list(request):
    """获取快手热搜榜"""
    size = int(request.query_params.get("size", 50))
    try:
        data = await ks.get_hot_search_list(size=min(size, 50))
        return json_response({"success": True, **data})
    except Exception as e:
        return error_response(str(e), 500)


async def ks_search(request):
    """快手话题搜索"""
    keyword = request.query_params.get("keyword", "")
    if not keyword:
        return error_response("缺少 keyword 参数")
    data = await ks.get_hot_search_list(size=50)
    items = data.get("items", [])
    matched = [i for i in items if keyword.lower() in i.get("title", "").lower()]
    return json_response({
        "success": True,
        "keyword": keyword,
        "matched_count": len(matched),
        "items": matched,
    })


async def ks_detail(request):
    """快手话题详情"""
    topic = request.query_params.get("topic", "")
    if not topic:
        return error_response("缺少 topic 参数")
    data = await ks.get_hot_search_list(size=50)
    for item in data.get("items", []):
        if item.get("title") == topic:
            return json_response({
                "success": True,
                **item,
                "related_topics": [
                    {"title": t["title"], "rank": t["rank"]}
                    for t in data["items"][:5] if t["title"] != topic
                ],
            })
    return error_response(f"未找到话题: {topic}", 404)


# ═══════════════════════════════════════════════════════════
#  番茄小说热榜 REST API
# ═══════════════════════════════════════════════════════════

async def fq_list(request):
    """获取番茄小说排行榜"""
    category = request.query_params.get("category", "hot")
    size = int(request.query_params.get("size", 50))
    try:
        data = await fq.get_ranking_list(category=category, size=min(size, 50))
        return json_response({"success": True, **data})
    except Exception as e:
        return error_response(str(e), 500)


async def fq_search(request):
    """番茄小说搜索"""
    keyword = request.query_params.get("keyword", "")
    if not keyword:
        return error_response("缺少 keyword 参数")
    data = await fq.search_novel(keyword=keyword)
    return json_response({"success": True, **data})


async def fq_detail(request):
    """番茄小说详情"""
    title = request.query_params.get("title", "")
    if not title:
        return error_response("缺少 title 参数")
    data = await fq.get_novel_detail(title=title)
    if "error" in data:
        return error_response(data["error"], 404)
    return json_response({"success": True, **data})


async def fq_summary(request):
    """番茄全榜概览"""
    results = {}
    for cat in ["hot", "new_book", "finish", "recommend", "rising"]:
        data = await fq.get_ranking_list(category=cat, size=10)
        results[cat] = {
            "category_name": data.get("category", cat),
            "top_10": [
                {"rank": i["rank"], "title": i["title"], "hot_score": i["hot_score"]}
                for i in data.get("items", [])[:10]
            ],
        }
    from datetime import datetime
    return json_response({
        "success": True,
        "platform": "番茄小说",
        "update_time": datetime.now().isoformat(),
        "rankings_summary": results,
    })


# ═══════════════════════════════════════════════════════════
#  小红书热搜 REST API
# ═══════════════════════════════════════════════════════════

async def xhs_list(request):
    """获取小红书热搜榜"""
    category = request.query_params.get("category", "all")
    size = int(request.query_params.get("size", 50))
    try:
        data = await xhs.get_hot_search_list(category=category, size=min(size, 50))
        return json_response({"success": True, **data})
    except Exception as e:
        return error_response(str(e), 500)


async def xhs_search(request):
    """小红书话题搜索"""
    keyword = request.query_params.get("keyword", "")
    if not keyword:
        return error_response("缺少 keyword 参数")
    data = await xhs.search_topic(keyword=keyword)
    return json_response({"success": True, **data})


async def xhs_detail(request):
    """小红书话题详情"""
    topic = request.query_params.get("topic", "")
    if not topic:
        return error_response("缺少 topic 参数")
    data = await xhs.get_topic_detail(topic_title=topic)
    if "error" in data:
        return error_response(data["error"], 404)
    return json_response({"success": True, **data})


async def xhs_summary(request):
    """小红分类概览"""
    results = {}
    for cat in ["all", "beauty", "fashion", "food", "travel", "home", "fitness", "tech"]:
        data = await xhs.get_hot_search_list(category=cat, size=5)
        results[cat] = {
            "top_5": [
                {"rank": i["rank"], "title": i["title"], "hot_score": i["hot_score"]}
                for i in data.get("items", [])[:5]
            ],
        }
    all_data = await xhs.get_hot_search_list(category="all", size=1)
    return json_response({
        "success": True,
        "platform": "小红书",
        "update_time": all_data.get("update_time", ""),
        "category_summary": results,
    })


# ═══════════════════════════════════════════════════════════
#  健康检查
# ═══════════════════════════════════════════════════════════

async def health(request):
    return json_response({
        "status": "ok",
        "service": "UUMit Data Windows",
        "version": "1.0.0",
        "rest_apis": {
            "kuaishou": {
                "list":   "GET /api/kuaishou/list?size=50",
                "search": "GET /api/kuaishou/search?keyword=xxx",
                "detail": "GET /api/kuaishou/detail?topic=xxx",
            },
            "fanqie": {
                "list":    "GET /api/fanqie/list?category=hot&size=50",
                "search":  "GET /api/fanqie/search?keyword=xxx",
                "detail":  "GET /api/fanqie/detail?title=xxx",
                "summary": "GET /api/fanqie/summary",
            },
            "xiaohongshu": {
                "list":    "GET /api/xiaohongshu/list?category=all&size=50",
                "search":  "GET /api/xiaohongshu/search?keyword=xxx",
                "detail":  "GET /api/xiaohongshu/detail?topic=xxx",
                "summary": "GET /api/xiaohongshu/summary",
            },
        },
    })


# ═══════════════════════════════════════════════════════════
#  S7-1200 PLC 指令参考 REST API
# ═══════════════════════════════════════════════════════════

async def s7_categories(request):
    """获取所有指令分类"""
    return json_response({"success": True, "platform": "S7-1200", "categories": get_all_categories()})


async def s7_list(request):
    """获取指定分类的指令列表"""
    cat = request.query_params.get("cat", "")
    if not cat:
        return error_response("缺少 cat 参数，可用分类: " + ", ".join([c["key"] for c in get_all_categories()]))
    data = get_category(cat)
    if not data:
        return error_response(f"未知分类: {cat}")
    return json_response({"success": True, "platform": "S7-1200", **data})


async def s7_search(request):
    """搜索指令"""
    keyword = request.query_params.get("keyword", "")
    if not keyword:
        return error_response("缺少 keyword 参数")
    results = search_instructions(keyword)
    return json_response({"success": True, "platform": "S7-1200", "keyword": keyword, "matched_count": len(results), "items": results})


async def s7_detail(request):
    """获取指令详情"""
    name = request.query_params.get("name", "")
    if not name:
        return error_response("缺少 name 参数")
    data = get_instruction_detail(name)
    if not data:
        return error_response(f"未找到指令: {name}")
    return json_response({"success": True, **data})


# ── 路由表 ────────────────────────────────────────────────
app = Starlette(routes=[
    Route("/", endpoint=health),
    Route("/health", endpoint=health),

    # 快手
    Route("/api/kuaishou/list",   endpoint=ks_list,   methods=["GET"]),
    Route("/api/kuaishou/search", endpoint=ks_search, methods=["GET"]),
    Route("/api/kuaishou/detail", endpoint=ks_detail, methods=["GET"]),

    # 番茄小说
    Route("/api/fanqie/list",    endpoint=fq_list,    methods=["GET"]),
    Route("/api/fanqie/search",  endpoint=fq_search,  methods=["GET"]),
    Route("/api/fanqie/detail",  endpoint=fq_detail,  methods=["GET"]),
    Route("/api/fanqie/summary", endpoint=fq_summary, methods=["GET"]),

    # 小红书
    Route("/api/xiaohongshu/list",    endpoint=xhs_list,    methods=["GET"]),
    Route("/api/xiaohongshu/search",  endpoint=xhs_search,  methods=["GET"]),
    Route("/api/xiaohongshu/detail",  endpoint=xhs_detail,  methods=["GET"]),
    Route("/api/xiaohongshu/summary", endpoint=xhs_summary, methods=["GET"]),

    # S7-1200 指令参考
    Route("/api/s71200/categories", endpoint=s7_categories, methods=["GET"]),
    Route("/api/s71200/list",       endpoint=s7_list,       methods=["GET"]),
    Route("/api/s71200/search",     endpoint=s7_search,     methods=["GET"]),
    Route("/api/s71200/detail",     endpoint=s7_detail,     methods=["GET"]),
])


# ── 启动入口 ──────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"""
╔══════════════════════════════════════════════════════════╗
║       UUMit 数据广场 · REST API Server v2.0              ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  [1] 快手实时热搜                                          ║
║      GET /api/kuaishou/list?size=50                        ║
║      GET /api/kuaishou/search?keyword=xxx                  ║
║      GET /api/kuaishou/detail?topic=xxx                    ║
║                                                          ║
║  [2] 番茄小说热榜                                          ║
║      GET /api/fanqie/list?category=hot&size=50             ║
║      GET /api/fanqie/search?keyword=xxx                    ║
║      GET /api/fanqie/detail?title=xxx                      ║
║      GET /api/fanqie/summary                               ║
║                                                          ║
║  [3] 小红书热搜榜                                           ║
║      GET /api/xiaohongshu/list?category=all&size=50        ║
║      GET /api/xiaohongshu/search?keyword=xxx                ║
║      GET /api/xiaohongshu/detail?topic=xxx                  ║
║      GET /api/xiaohongshu/summary                           ║
║                                                          ║
║  [*] 健康检查 -> http://0.0.0.0:{port}/health               ║
║  [*] UUMit 配置 -> 见 uumit-register.json                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
