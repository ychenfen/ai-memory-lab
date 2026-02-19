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

if __name__ == '__main__':
    import os
    main()
