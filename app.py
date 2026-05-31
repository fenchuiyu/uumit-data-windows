"""
PythonAnywhere WSGI 适配版本
兼容 PythonAnywhere 免费主机
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify
import json

from kuaishou_hotsearch.scraper import KuaishouHotSearchScraper
from fanqie_novel.scraper import FanqieNovelScraper
from xiaohongshu_hotsearch.scraper import XiaohongshuHotSearchScraper

app = Flask(__name__)

ks = KuaishouHotSearchScraper()
fq = FanqieNovelScraper()
xhs = XiaohongshuHotSearchScraper()

@app.route("/")
@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "UUMit Data Windows", "version": "2.0"})

# ── 快手 ──
@app.route("/api/kuaishou/list")
def ks_list():
    size = min(int(request.args.get("size", 50)), 50)
    return _async(ks.get_hot_search_list(size=size))

@app.route("/api/kuaishou/search")
def ks_search():
    kw = request.args.get("keyword", "")
    if not kw:
        return jsonify({"error": "missing keyword"}), 400
    return _async(_ks_search(kw))

@app.route("/api/kuaishou/detail")
def ks_detail():
    topic = request.args.get("topic", "")
    if not topic:
        return jsonify({"error": "missing topic"}), 400
    return _async(_ks_detail(topic))

async def _ks_search(kw):
    data = await ks.get_hot_search_list(size=50)
    items = data.get("items", [])
    matched = [i for i in items if kw.lower() in i.get("title", "").lower()]
    return {"success": True, "keyword": kw, "matched_count": len(matched), "items": matched}

async def _ks_detail(topic):
    data = await ks.get_hot_search_list(size=50)
    for item in data.get("items", []):
        if item.get("title") == topic:
            return {"success": True, **item}
    return {"error": f"not found: {topic}"}, 404

# ── 番茄 ──
@app.route("/api/fanqie/list")
def fq_list():
    cat = request.args.get("category", "hot")
    size = min(int(request.args.get("size", 50)), 50)
    return _async(fq.get_ranking_list(category=cat, size=size))

@app.route("/api/fanqie/search")
def fq_search():
    kw = request.args.get("keyword", "")
    if not kw: return jsonify({"error": "missing keyword"}), 400
    return _async(fq.search_novel(keyword=kw))

@app.route("/api/fanqie/detail")
def fq_detail():
    title = request.args.get("title", "")
    if not title: return jsonify({"error": "missing title"}), 400
    return _async(fq.get_novel_detail(title=title))

@app.route("/api/fanqie/summary")
def fq_summary():
    return _async(_fq_summary())

async def _fq_summary():
    from datetime import datetime
    results = {}
    for cat in ["hot", "new_book", "finish", "recommend", "rising"]:
        data = await fq.get_ranking_list(category=cat, size=10)
        results[cat] = {"category_name": data.get("category", cat), "top_10": [
            {"rank": i["rank"], "title": i["title"], "hot_score": i["hot_score"]}
            for i in data.get("items", [])[:10]
        ]}
    return {"success": True, "platform": "番茄小说", "update_time": datetime.now().isoformat(), "rankings_summary": results}

# ── 小红书 ──
@app.route("/api/xiaohongshu/list")
def xhs_list():
    cat = request.args.get("category", "all")
    size = min(int(request.args.get("size", 50)), 50)
    return _async(xhs.get_hot_search_list(category=cat, size=size))

@app.route("/api/xiaohongshu/search")
def xhs_search():
    kw = request.args.get("keyword", "")
    if not kw: return jsonify({"error": "missing keyword"}), 400
    return _async(xhs.search_topic(keyword=kw))

@app.route("/api/xiaohongshu/detail")
def xhs_detail():
    topic = request.args.get("topic", "")
    if not topic: return jsonify({"error": "missing topic"}), 400
    return _async(xhs.get_topic_detail(topic_title=topic))

@app.route("/api/xiaohongshu/summary")
def xhs_summary():
    return _async(_xhs_summary())

async def _xhs_summary():
    results = {}
    for cat in ["all", "beauty", "fashion", "food", "travel", "home", "fitness", "tech"]:
        data = await xhs.get_hot_search_list(category=cat, size=5)
        results[cat] = {"top_5": [
            {"rank": i["rank"], "title": i["title"], "hot_score": i["hot_score"]}
            for i in data.get("items", [])[:5]
        ]}
    all_data = await xhs.get_hot_search_list(category="all", size=1)
    return {"success": True, "platform": "小红书", "update_time": all_data.get("update_time", ""), "category_summary": results}

def _async(coro):
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    result = loop.run_until_complete(coro)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
