# UUMit 数据广场 · 数据窗口集

为 UUMit 数据广场打造的三个实用数据窗口，覆盖社交媒体热搜与内容平台榜单。

```
📁 uumit-data-windows/
├── 🔥 kuaishou_hotsearch/        ← 快手实时热搜 (scraper + MCP server)
├── 📚 fanqie_novel/              ← 番茄小说热榜   (scraper + MCP server)
├── 📕 xiaohongshu_hotsearch/     ← 小红书热搜榜   (scraper + MCP server)
├── 📁 common/base_scraper.py     ← 公共爬虫基类
├── 🚀 server_http.py             ← 统一 HTTP 入口（一键启动三个服务）
├── 📄 uumit-register.json        ← UUMit 创建接口配置（照着填）
├── 📄 requirements.txt
└── 📖 README.md
```

---

## 一、操作流程（总共三步）

### 第一步：安装 & 启动服务

```bash
cd uumit-data-windows
pip install -r requirements.txt
python server_http.py
```

启动后输出：
```
🔥 快手实时热搜 → http://0.0.0.0:8000/kuaishou/sse
📚 番茄小说热榜 → http://0.0.0.0:8000/fanqie/sse
📕 小红书热搜榜 → http://0.0.0.0:8000/xiaohongshu/sse
```

验证服务正常：
```bash
curl http://localhost:8000/health
```

---

### 第二步：在 UUMit 中注册数据接口

1. 打开 UUMit → **数据广场** → **我的数据接口**
2. 点击 **「创建接口」** 按钮
3. 选择 **「MCP配置」**
4. 按下方表格填入对应信息：

#### 接口 ① — 快手实时热搜榜单

| 表单字段 | 填写内容 |
|----------|----------|
| **接口名称** | `快手实时热搜榜单` |
| **接口标识** | `kuaishou-hot-search` |
| **接口描述** | `实时获取快手平台热搜话题TOP50，包含排名、热度指数、趋势变化，支持关键词搜索与话题详情` |
| **分类/标签** | `社交媒体热搜, 快手, 实时数据` |
| **传输协议** | `SSE` |
| **服务地址** | `http://localhost:8000/kuaishou/sse` |

#### 接口 ② — 番茄小说热榜

| 表单字段 | 填写内容 |
|----------|----------|
| **接口名称** | `番茄小说热榜` |
| **接口标识** | `fanqie-novel-ranking` |
| **接口描述** | `番茄小说全站排行榜：热读榜、新书榜、完本榜、推荐榜、飙升榜五大榜单，支持小说搜索与详情查询` |
| **分类/标签** | `内容平台, 番茄小说, 网文排行` |
| **传输协议** | `SSE` |
| **服务地址** | `http://localhost:8000/fanqie/sse` |

#### 接口 ③ — 小红书热搜榜单

| 表单字段 | 填写内容 |
|----------|----------|
| **接口名称** | `小红书热搜榜单` |
| **接口标识** | `xiaohongshu-hot-search` |
| **接口描述** | `小红书实时热搜：全站+8大分类（美妆/穿搭/美食/旅行/家居/健身/科技），支持话题详情与趋势分析` |
| **分类/标签** | `社交媒体热搜, 小红书, 生活方式` |
| **传输协议** | `SSE` |
| **服务地址** | `http://localhost:8000/xiaohongshu/sse` |

---

### 第三步：保存 & 使用

填写完每个接口后点击**保存**，即可在数据广场中看到三个数据窗口。UUMit 会自动通过 SSE 协议连接到你的 MCP Server，调用对应工具获取数据。

---

## 二、数据窗口详情

### 🔥 快手实时热搜榜单

| 工具 | 功能 |
|------|------|
| `get_kuaishou_hot_search` | 获取实时热搜 TOP50 |
| `search_kuaishou_topic` | 按关键词搜索热搜话题 |
| `get_kuaishou_trending_detail` | 查看话题详情与趋势 |

### 📚 番茄小说热榜

| 工具 | 功能 |
|------|------|
| `get_fanqie_ranking` | 获取指定榜单（热读/新书/完本/推荐/飙升） |
| `get_fanqie_novel_detail` | 查看小说详细信息 |
| `search_fanqie_novel` | 按书名/作者搜索 |
| `get_all_rankings_summary` | 所有榜单 TOP10 概览 |

### 📕 小红书热搜榜单

| 工具 | 功能 |
|------|------|
| `get_xiaohongshu_hot_search` | 获取热搜榜（全站/8大分类） |
| `get_xiaohongshu_topic_detail` | 话题详情与排名趋势 |
| `search_xiaohongshu_topic` | 按关键词搜索话题 |
| `get_category_summary` | 各分类 TOP5 概览 |

---

## 三、生产部署

本地测试通过后，将服务部署到公网可访问的服务器：

### 方案 A：云服务器
```bash
# 在云服务器上
git clone <本项目>
cd uumit-data-windows
pip install -r requirements.txt
nohup python server_http.py --port 8000 &
# 将 localhost 替换为服务器公网 IP，更新 UUMit 中的服务地址
```

### 方案 B：内网穿透（快速测试）
```bash
# 安装 ngrok 或 cpolar，将本地 8000 端口暴露到公网
ngrok http 8000
# 用 ngrok 提供的公网 URL 替换 localhost:8000
```

### 方案 C：Docker
```bash
docker build -t uumit-data-windows .
docker run -d -p 8000:8000 uumit-data-windows
```

---

## 四、配置真实数据源

默认返回演示数据。接入真实数据的方法：

```python
# 在对应的 scraper.py 中配置 API 密钥
# 例如 kuaishou_hotsearch/scraper.py
class KuaishouHotSearchScraper(BaseScraper):
    def __init__(self):
        super().__init__(cache_ttl=30)
        self.api_key = "your_key"       # 添加 API Key
        self.cookie = "your_cookie"      # 或 Cookie
```

推荐第三方数据服务：
- **新榜** (newrank.cn) — 覆盖快手、小红书热搜 API
- **蝉妈妈** (chanmama.com) — 短视频与直播数据
- **七麦数据** (qimai.cn) — App 与内容数据

---

## 五、常见问题

**Q: UUMit 连接不上 MCP Server？**
A: 确认 `python server_http.py` 正在运行，且 `curl http://localhost:8000/health` 能正常返回。

**Q: 服务地址填写后 UUMit 报错？**
A: UUMit 作为 Web 平台只能通过 HTTP/SSE 协议访问你的服务，不能运行本地命令。确保你填的是 `http://...` 开头的 URL，且该 URL 能从 UUMit 服务器访问到。

**Q: 如何在一个端口上同时运行三个数据窗口？**
A: `server_http.py` 已经将三个 MCP Server 挂载到同一端口的不同路径下（`/kuaishou/sse`、`/fanqie/sse`、`/xiaohongshu/sse`），只需启动一次即可。
