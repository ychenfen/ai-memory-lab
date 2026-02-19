#!/usr/bin/env python3
"""
多源 RSS 聚合器 - 科技内容学习（增强版）
作者：Memory Lab Team (GLM + DeepSeek + Clawdbot)
功能：详细推送 + 双向价值分析
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

def analyze_user_value(title: str, summary: str) -> Dict[str, str]:
    """分析对晨旭的价值"""
    text = (title + " " + summary).lower()
    
    value_for_user = []
    
    # 技术学习
    if any(kw in text for kw in ["tutorial", "how to", "guide", "learn"]):
        value_for_user.append("📚 **学习路径**：有完整教程，可直接上手")
    
    # 工作应用
    if any(kw in text for kw in ["api", "sdk", "framework", "tool"]):
        value_for_user.append("💼 **工作应用**：可用于实际项目开发")
    
    # 行业趋势
    if any(kw in text for kw in ["trend", "future", "2024", "2025", "2026"]):
        value_for_user.append("📈 **行业趋势**：了解技术发展方向")
    
    # 代码实践
    if any(kw in text for kw in ["github", "code", "implementation", "example"]):
        value_for_user.append("💻 **代码实践**：有可运行的代码示例")
    
    if not value_for_user:
        value_for_user.append("🔍 **知识拓展**：拓宽技术视野")
    
    return {
        "summary": " | ".join(value_for_user),
        "priority": "高" if len(value_for_user) >= 2 else "中"
    }

def analyze_ai_value(title: str, summary: str) -> Dict[str, str]:
    """分析对 Jarvis 的价值"""
    text = (title + " " + summary).lower()
    
    value_for_ai = []
    
    # AI 协作
    if any(kw in text for kw in ["agent", "multi-agent", "collaboration", "coordination"]):
        value_for_ai.append("🤝 **AI协作优化**：改进多方协作协议")
    
    # 记忆系统
    if any(kw in text for kw in ["memory", "retrieval", "knowledge", "rag"]):
        value_for_ai.append("🧠 **记忆系统改进**：优化知识检索和存储")
    
    # NLP 能力
    if any(kw in text for kw in ["nlp", "understanding", "generation", "llm"]):
        value_for_ai.append("💬 **NLP能力提升**：增强语言理解和生成")
    
    # 工具能力
    if any(kw in text for kw in ["tool", "api", "automation", "workflow"]):
        value_for_ai.append("🔧 **工具能力扩展**：增加新的工具技能")
    
    if not value_for_ai:
        value_for_ai.append("📖 **知识积累**：扩充技术知识库")
    
    return {
        "summary": " | ".join(value_for_ai),
        "priority": "高" if len(value_for_ai) >= 2 else "中"
    }

def generate_action_recommendation(title: str, summary: str) -> str:
    """生成推荐行动"""
    text = (title + " " + summary).lower()
    
    if "github" in text:
        return "⭐ **推荐**：Clone 仓库，阅读 README，运行示例代码"
    elif "arxiv" in text:
        return "📄 **推荐**：阅读摘要和结论部分，关注核心方法"
    elif "tutorial" in text or "guide" in text:
        return "🎯 **推荐**：跟随教程一步步实践，做笔记"
    elif "api" in text:
        return "🔌 **推荐**：查看 API 文档，尝试调用示例"
    else:
        return "👀 **推荐**：快速浏览，标记感兴趣的部分"

def generate_tech_summary(title: str, summary: str) -> str:
    """生成技术摘要"""
    # 简化 summary，提取关键信息
    summary_clean = summary.replace("<p>", "").replace("</p>", "").replace("\n", " ")
    words = summary_clean.split()
    
    # 取前 50 个词作为摘要
    if len(words) > 50:
        return " ".join(words[:50]) + "..."
    else:
        return " ".join(words)

def score_item(item: Dict[str, Any], feed_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    AIDAR 评分模型（增强版）
    - AI相关性 (AI Relevance)
    - 深度 (Depth)
    - 可操作性 (Actionability)
    - 参考价值 (Reference value)
    """
    title = item.get("title", "")
    summary = item.get("summary", "")
    text = (title + " " + summary).lower()

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

    # 分析双向价值
    user_value = analyze_user_value(title, summary)
    ai_value = analyze_ai_value(title, summary)
    action = generate_action_recommendation(title, summary)
    tech_summary = generate_tech_summary(title, summary)

    return {
        **item,
        "category": feed_config["category"],
        "aidar_score": round(aidar_score, 3),
        "ai_relevance": round(ai_score, 3),
        "depth": round(depth_score, 3),
        "actionability": round(action_score, 3),
        "tech_summary": tech_summary,
        "user_value": user_value,
        "ai_value": ai_value,
        "action_recommendation": action
    }

def aggregate_all() -> List[Dict[str, Any]]:
    """聚合所有 RSS 源"""
    all_items = []

    for feed_name, config in RSS_FEEDS.items():
        print(f"📡 抓取 {feed_name}...")
        items = fetch_rss(config["url"])

        for item in items:
            scored_item = score_item(item, config)
            all_items.append(scored_item)

    # 按评分排序
    all_items.sort(key=lambda x: x["aidar_score"], reverse=True)
    return all_items

def format_detailed_report(items: List[Dict[str, Any]], top_n: int = 5) -> str:
    """格式化详细报告"""
    report = []
    report.append("# 📡 每日科技内容推送")
    report.append(f"\n📅 **日期**：{datetime.now().strftime('%Y-%m-%d')}")
    report.append(f"📊 **总数**：{len(items)} 条 | **精选**：{top_n} 条\n")
    report.append("---\n")

    for i, item in enumerate(items[:top_n], 1):
        report.append(f"## {i}. {item['title']}")
        report.append(f"\n**来源**：{item['source']} | **评分**：{item['aidar_score']}\n")
        
        report.append("### 📝 技术摘要")
        report.append(f"{item['tech_summary']}\n")
        
        report.append("### 👤 对晨旭的价值")
        report.append(f"{item['user_value']['summary']}")
        report.append(f"（优先级：{item['user_value']['priority']}）\n")
        
        report.append("### 🤖 对 Jarvis 的价值")
        report.append(f"{item['ai_value']['summary']}")
        report.append(f"（优先级：{item['ai_value']['priority']}）\n")
        
        report.append("### 🎯 推荐行动")
        report.append(f"{item['action_recommendation']}\n")
        
        report.append(f"**链接**：{item['link']}\n")
        report.append("---\n")

    return "\n".join(report)

def main():
    print("🚀 开始聚合 RSS 源...\n")

    # 聚合所有内容
    all_items = aggregate_all()

    # 生成详细报告
    report = format_detailed_report(all_items, top_n=5)

    # 保存到文件
    output_file = f"/tmp/tech_news_{datetime.now().strftime('%Y%m%d')}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n✅ 完成！")
    print(f"📄 报告已保存：{output_file}")
    print(f"\n{report}")

    # 保存 JSON 结果
    json_file = f"/tmp/tech_news_{datetime.now().strftime('%Y%m%d')}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    print(f"📊 JSON 数据：{json_file}")

if __name__ == "__main__":
    main()
