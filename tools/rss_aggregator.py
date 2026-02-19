#!/usr/bin/env python3
"""
多源 RSS 聚合器 - 科技内容学习
作者：Memory Lab Team (GLM + DeepSeek + Clawdbot)
"""

import feedparser
import json
from datetime import datetime
from typing import List, Dict, Any

# RSS 源配置
RSS_FEEDS = {
    "hackernews": {
        "url": "https://hnrss.org/frontpage",
        "category": "技术深度",
        "weight": 1.0
    },
    "github_trending": {
        "url": "https://mshibanami.github.io/GitHubTrendingRSS/daily.xml",
        "category": "代码实践",
        "weight": 0.9
    },
    "arxiv_ai": {
        "url": "http://export.arxiv.org/rss/cs.AI",
        "category": "AI前沿",
        "weight": 0.8
    },
    "arxiv_cl": {
        "url": "http://export.arxiv.org/rss/cs.CL",
        "category": "NLP前沿",
        "weight": 0.8
    }
}

def fetch_rss(feed_url: str) -> List[Dict[str, Any]]:
    """抓取单个 RSS feed"""
    try:
        feed = feedparser.parse(feed_url)
        items = []
        for entry in feed.entries[:10]:  # 每个源取前10条
            items.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", ""),
                "source": feed.feed.get("title", "Unknown")
            })
        return items
    except Exception as e:
        print(f"❌ 抓取失败 {feed_url}: {e}")
        return []

def score_item(item: Dict[str, Any], feed_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    AIDAR 评分模型
    - AI相关性 (AI Relevance)
    - 深度 (Depth)
    - 可操作性 (Actionability)
    - 参考价值 (Reference value)
    """
    title = item.get("title", "").lower()
    summary = item.get("summary", "").lower()
    text = title + " " + summary

    # AI 相关性关键词
    ai_keywords = ["ai", "machine learning", "deep learning", "nlp", "llm",
                   "gpt", "transformer", "neural", "agent", "memory"]
    ai_score = sum(1 for kw in ai_keywords if kw in text) / len(ai_keywords)

    # 深度关键词
    depth_keywords = ["architecture", "algorithm", "system", "design",
                      "implementation", "optimization", "performance"]
    depth_score = sum(1 for kw in depth_keywords if kw in text) / len(depth_keywords)

    # 可操作性
    action_keywords = ["github", "code", "tutorial", "how to", "guide", "example"]
    action_score = sum(1 for kw in action_keywords if kw in text) / len(action_keywords)

    # 综合评分
    aidar_score = (ai_score * 0.4 + depth_score * 0.3 + action_score * 0.3) * feed_config["weight"]

    return {
        **item,
        "category": feed_config["category"],
        "aidar_score": round(aidar_score, 3),
        "ai_relevance": round(ai_score, 3),
        "depth": round(depth_score, 3),
        "actionability": round(action_score, 3)
    }

def aggregate_all() -> List[Dict[str, Any]]:
    """聚合所有 RSS 源"""
    all_items = []

    for feed_name, config in RSS_FEEDS.items():
        print(f"📡 抓取 {feed_name}...")
        items = fetch_rss(config["url"])

        for item in items:
            scored = score_item(item, config)
            all_items.append(scored)

        print(f"   ✅ {len(items)} 条")

    # 按评分排序
    all_items.sort(key=lambda x: x["aidar_score"], reverse=True)

    return all_items

def format_item(item: Dict[str, Any]) -> str:
    """格式化单条内容"""
    emoji = "🔥" if item["aidar_score"] > 0.3 else "📌"

    ai_note = "✓ AI相关" if item["ai_relevance"] > 0.1 else ""
    depth_note = "✓ 深度" if item["depth"] > 0.1 else ""
    action_note = "✓ 可操作" if item["actionability"] > 0.1 else ""

    tags = " ".join([t for t in [ai_note, depth_note, action_note] if t])

    return f"""{emoji} **{item['title']}**
📂 {item['category']} | 评分: {item['aidar_score']} {tags}
🔗 {item['link']}
"""

def analyze_value_for_user(item: Dict[str, Any]) -> Dict[str, List[str]]:
    """分析对用户的价值"""
    title = item.get("title", "").lower()
    summary = item.get("summary", "").lower()
    text = title + " " + summary
    
    values = []
    
    # 技术学习
    if any(kw in text for kw in ["tutorial", "how to", "guide", "implement"]):
        values.append("📚 技术教程")
    
    # 创业灵感
    if any(kw in text for kw in ["startup", "business", "product", "market"]):
        values.append("💡 创业灵感")
    
    # 投资决策
    if any(kw in text for kw in ["trend", "future", "prediction", "analysis"]):
        values.append("📊 趋势分析")
    
    # AI前沿
    if any(kw in text for kw in ["llm", "gpt", "transformer", "agent"]):
        values.append("🤖 AI前沿")
    
    # 代码实践
    if any(kw in text for kw in ["github", "code", "library", "tool"]):
        values.append("💻 代码实践")
    
    return {
        "values": values if values else ["📖 一般资讯"],
        "actionable": "✅ 可直接应用" if item["actionability"] > 0.2 else "📚 建议学习"
    }

def analyze_value_for_glm(item: Dict[str, Any]) -> Dict[str, List[str]]:
    """分析对 GLM 的价值"""
    title = item.get("title", "").lower()
    summary = item.get("summary", "").lower()
    text = title + " " + summary
    
    values = []
    
    # 记忆系统
    if any(kw in text for kw in ["memory", "retrieval", "context", "attention"]):
        values.append("🧠 改进记忆检索")
    
    # 多AI协作
    if any(kw in text for kw in ["agent", "multi-agent", "collaboration", "coordination"]):
        values.append("🤝 优化AI协作")
    
    # NLP能力
    if any(kw in text for kw in ["nlp", "language", "generation", "understanding"]):
        values.append("💬 增强语言能力")
    
    # 工具集成
    if any(kw in text for kw in ["tool", "api", "integration", "automation"]):
        values.append("🔧 工具集成")
    
    # 知识管理
    if any(kw in text for kw in ["knowledge", "graph", "embedding", "vector"]):
        values.append("📚 知识管理")
    
    return {
        "values": values if values else ["📖 一般参考"],
        "integrable": "✅ 可集成到 Memory Lab" if item["ai_relevance"] > 0.2 else "📚 可学习参考"
    }

def format_for_telegram(top_items: List[Dict[str, Any]]) -> str:
    """格式化为 Telegram 消息（详细版）"""
    msg = "🧠 **每日科技精选**\n"
    msg += f"📅 {datetime.now().strftime('%Y-%m-%d')}\n"
    msg += "─" * 30 + "\n\n"

    for i, item in enumerate(top_items, 1):
        emoji = "🔥" if item["aidar_score"] > 0.3 else "📌"
        msg += f"{i}. {emoji} **{item['title'][:80]}**\n"
        msg += f"   📂 {item['category']} | 评分 {item['aidar_score']}\n\n"
        
        # 对用户的价值
        user_value = analyze_value_for_user(item)
        msg += f"   **对你的价值**：\n"
        for v in user_value["values"][:3]:
            msg += f"   • {v}\n"
        msg += f"   • {user_value['actionable']}\n\n"
        
        # 对 GLM 的价值
        glm_value = analyze_value_for_glm(item)
        msg += f"   **对 GLM 的价值**：\n"
        for v in glm_value["values"][:3]:
            msg += f"   • {v}\n"
        msg += f"   • {glm_value['integrable']}\n\n"
        
        msg += f"   🔗 {item['link']}\n"
        msg += "─" * 30 + "\n\n"

    msg += "🤖 Memory Lab Team (GLM + DeepSeek + Clawdbot)"

    return msg

def send_to_telegram(message: str) -> bool:
    """发送到 Telegram（通过 clawdbot）"""
    try:
        import requests
        # 使用本地 clawdbot API
        response = requests.post(
            "http://localhost:3000/api/send",
            json={
                "channel": "telegram",
                "message": message
            },
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Telegram 推送失败: {e}")
        return False

def main():
    print("🧠 多源 RSS 聚合器 - 科技内容学习")
    print("=" * 60)

    # 聚合
    items = aggregate_all()

    print(f"\n✅ 共 {len(items)} 条内容")
    print(f"📊 筛选 Top 10（评分 > 0.2）:\n")

    # 筛选 Top 10
    top_items = [i for i in items if i["aidar_score"] > 0.2][:10]

    for i, item in enumerate(top_items, 1):
        print(f"{i}. {format_item(item)}")

    # 保存
    output_path = "~/clawd-glm/cache/rss_aggregated.json"
    output_path = os.path.expanduser(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(items),
            "top_items": top_items
        }, f, indent=2, ensure_ascii=False)

    print(f"\n💾 已保存到 {output_path}")

    # Telegram 推送
    if top_items:
        msg = format_for_telegram(top_items)
        if send_to_telegram(msg):
            print("✅ 已推送到 Telegram")
        else:
            print("⚠️ Telegram 推送失败，内容已保存")

if __name__ == '__main__':
    import os
    main()
