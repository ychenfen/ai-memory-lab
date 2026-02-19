#!/usr/bin/env python3
"""
Tech News Pro - 科技资讯聚合器增强版

功能：
  - 多源获取：科技博主 + For You 推荐
  - 智能翻译：分段翻译，更准确
  - 价值识别：AI 分析重要性
  - 内容去重：避免重复
  - 格式优化：清晰的阅读体验
"""

import subprocess
import json
import sys
import os
import time
import re
from datetime import datetime
from pathlib import Path

# 翻译
from deep_translator import GoogleTranslator

# 导入 media_grab
sys.path.insert(0, str(Path(__file__).parent))
from media_grab import TwitterGrabber

# ==================== 科技博主列表（扩展） ====================

TECH_ACCOUNTS = {
    # === AI/ML 核心人物 ===
    "karpathy": {"name": "Andrej Karpathy", "desc": "AI/ML 专家，前 Tesla AI 总监", "priority": 5, "category": "AI技术"},
    "sama": {"name": "Sam Altman", "desc": "OpenAI CEO", "priority": 5, "category": "AI公司"},
    "gdb": {"name": "Greg Brockman", "desc": "OpenAI 联合创始人", "priority": 4, "category": "AI公司"},
    "ylecun": {"name": "Yann LeCun", "desc": "AI 教父，Meta AI 首席科学家", "priority": 5, "category": "AI技术"},
    "AndrewYNg": {"name": "Andrew Ng", "desc": "AI 教育先驱", "priority": 4, "category": "AI技术"},
    "goodfellow_ian": {"name": "Ian Goodfellow", "desc": "GAN 发明者，Apple ML", "priority": 3, "category": "AI技术"},
    "demishassabis": {"name": "Demis Hassabis", "desc": "DeepMind CEO", "priority": 5, "category": "AI技术"},
    "jeffdean": {"name": "Jeff Dean", "desc": "Google AI 负责人", "priority": 4, "category": "AI技术"},
    "doriangpt": {"name": "Dorian Pyle", "desc": "AI 研究员", "priority": 3, "category": "AI技术"},
    
    # === 创业/投资 ===
    "paulg": {"name": "Paul Graham", "desc": "Y Combinator 创始人", "priority": 5, "category": "创业投资"},
    "naval": {"name": "Naval Ravikant", "desc": "投资人/哲学家", "priority": 5, "category": "个人成长"},
    "patrickc": {"name": "Patrick Collison", "desc": "Stripe CEO", "priority": 4, "category": "创业投资"},
    "elerianm": {"name": "Mohamed El-Erian", "desc": "经济学家", "priority": 3, "category": "投资"},
    "balajis": {"name": "Balaji Srinivasan", "desc": "创业者/投资人", "priority": 4, "category": "创业投资"},
    "packym": {"name": "Packy McCormick", "desc": "Not Boring 作者", "priority": 4, "category": "创业投资"},
    "cburniske": {"name": "Chris Burniske", "desc": "a16z 加密", "priority": 3, "category": "投资"},
    
    # === 技术/编程 ===
    "antirez": {"name": "Salvatore Sanfilippo", "desc": "Redis 作者", "priority": 3, "category": "技术编程"},
    "pgbovine": {"name": "Philip Guo", "desc": "编程教育", "priority": 3, "category": "技术编程"},
    "swyx": {"name": "Shawn Wang", "desc": "AI 开发者", "priority": 4, "category": "AI技术"},
    "fchollet": {"name": "François Chollet", "desc": "Keras 作者", "priority": 4, "category": "AI技术"},
    
    # === 科技公司 ===
    "elonmusk": {"name": "Elon Musk", "desc": "Tesla/SpaceX/X", "priority": 5, "category": "AI公司"},
    "satlopz": {"name": "Satya Nadella", "desc": "Microsoft CEO", "priority": 4, "category": "AI公司"},
    "sundarpichai": {"name": "Sundar Pichai", "desc": "Google CEO", "priority": 4, "category": "AI公司"},
    "tim_cook": {"name": "Tim Cook", "desc": "Apple CEO", "priority": 3, "category": "AI公司"},
    
    # === 科技媒体 ===
    "CaseyNewton": {"name": "Casey Newton", "desc": "Platformer", "priority": 3, "category": "科技媒体"},
    "reckless": {"name": "Nilay Patel", "desc": "The Verge", "priority": 3, "category": "科技媒体"},
    "benedictevans": {"name": "Benedict Evans", "desc": "科技分析师", "priority": 4, "category": "科技媒体"},
}

# 默认博主（按优先级）
DEFAULT_ACCOUNTS = [
    # Priority 5
    "karpathy", "sama", "ylecun", "paulg", "naval", "demishassabis", "elonmusk",
    # Priority 4
    "swyx", "fchollet", "patrickc", "balajis", "packym", "gdb", "AndrewYNg",
    "benedictevans", "jeffdean"
]

# ==================== 高价值关键词 ====================

VALUABLE_PATTERNS = {
    # AI/ML 突破
    "breakthrough": ["breakthrough", "突破", "革命性", "landmark", "milestone"],
    "release": ["release", "launch", "announce", "发布", "推出", "上线"],
    "agi": ["AGI", "general intelligence", "通用人工智能"],
    
    # 产品更新
    "codex": ["codex", "openclaw", "gpt", "claude", "gemini", "llama"],
    "new_feature": ["new feature", "update", "更新", "新功能"],
    
    # 重大事件
    "funding": ["raise", "funding", "融资", "投资"],
    "acquisition": ["acquire", "merge", "收购", "合并"],
    
    # 技术趋势
    "trend": ["future", "趋势", "next", "新兴"],
}

# 过滤关键词（噪音）
NOISE_PATTERNS = [
    " giveaway", "contest", "winner", "congratulations to",
    "just followed", "following back", "dm me", "check my",
    "赚大钱", "免费领取", "关注有礼"
]

# ==================== 翻译优化 ====================

def smart_translate(text, target_lang='zh-CN'):
    """智能翻译：分段处理，提高准确性"""
    if not text or len(text) < 5:
        return text
    
    # 如果主要是中文，跳过
    chinese_ratio = len(re.findall(r'[\u4e00-\u9fff]', text)) / len(text)
    if chinese_ratio > 0.3:
        return text
    
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        
        # 分段翻译（避免长文本翻译不准确）
        if len(text) > 500:
            paragraphs = text.split('\n\n')
            translated = []
            for p in paragraphs:
                if len(p) > 400:
                    # 再分段
                    sentences = re.split(r'([.!?。！？])', p)
                    chunks = []
                    current = ""
                    for i in range(0, len(sentences), 2):
                        s = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else "")
                        if len(current) + len(s) < 400:
                            current += s
                        else:
                            if current:
                                chunks.append(current)
                            current = s
                    if current:
                        chunks.append(current)
                    
                    for chunk in chunks:
                        translated.append(translator.translate(chunk))
                else:
                    translated.append(translator.translate(p))
            return '\n\n'.join(translated)
        else:
            return translator.translate(text)
    except Exception as e:
        return f"[翻译失败]"

# ==================== 价值判断 ====================

def calculate_value_score(tweet):
    """计算推文价值分数 (0-100)"""
    text = tweet.get("text", "").lower()
    score = 0
    
    # 关键词匹配
    for category, keywords in VALUABLE_PATTERNS.items():
        for kw in keywords:
            if kw.lower() in text:
                if category in ["breakthrough", "agi", "release"]:
                    score += 20
                elif category in ["codex", "funding", "acquisition"]:
                    score += 15
                else:
                    score += 10
    
    # 作者权重
    author = tweet.get("author", "")
    if author in TECH_ACCOUNTS:
        score += TECH_ACCOUNTS[author].get("priority", 0) * 5
    
    # 互动数据（如果有）
    likes = tweet.get("favorite_count", 0)
    if likes > 10000:
        score += 15
    elif likes > 1000:
        score += 10
    elif likes > 100:
        score += 5
    
    # 去噪
    for noise in NOISE_PATTERNS:
        if noise.lower() in text:
            score -= 30
    
    return max(0, min(100, score))

# ==================== 内容去重 ====================

def deduplicate_tweets(tweets):
    """去重：基于文本相似度"""
    seen_texts = set()
    unique = []
    
    for tweet in tweets:
        text = tweet.get("text", "")
        # 简化文本用于比较
        simplified = re.sub(r'\s+', '', text.lower())[:100]
        
        if simplified not in seen_texts:
            seen_texts.add(simplified)
            unique.append(tweet)
    
    return unique

# ==================== 简报生成器 ====================

class TechNewsPro:
    def __init__(self):
        self.grabber = TwitterGrabber()
        self.cache_dir = Path.home() / ".cache" / "tech_news"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.cache_dir / "state.json"
        self.load_state()
    
    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {"seen_ids": [], "last_report": None}
    
    def save_state(self):
        """保存状态"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f)
    
    def get_account_tweets(self, username, count=2):
        """获取单个账号的推文"""
        print(f"  📥 @{username}...", flush=True)
        try:
            tweets = self.grabber.get_tweets_safari(username, count)
            # 过滤已看过的
            new_tweets = []
            for t in tweets:
                if t.get("link") and t["link"] not in self.state["seen_ids"]:
                    new_tweets.append(t)
            return new_tweets
        except Exception as e:
            print(f"    ✗ {e}", flush=True)
            return []
    
    def generate_report(self, accounts=None, count_per_account=2, limit=7):
        """生成科技简报"""
        if accounts is None:
            accounts = DEFAULT_ACCOUNTS
        
        print("\n" + "=" * 60)
        print(f"📰 科技简报 Pro - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
        print(f"📊 数据源: {len(accounts)} 个博主，每博主 {count_per_account} 条")
        
        # 获取推文
        all_tweets = []
        for i, username in enumerate(accounts):
            if i >= 10:  # 限制数量避免太慢
                break
            desc = TECH_ACCOUNTS.get(username, {})
            tweets = self.get_account_tweets(username, count_per_account)
            
            for tweet in tweets:
                tweet["author"] = username
                tweet["author_info"] = desc
                tweet["value_score"] = calculate_value_score(tweet)
            
            all_tweets.extend(tweets)
            time.sleep(0.5)  # 礼貌性延迟
        
        if not all_tweets:
            print("\n⚠️  未获取到新内容")
            return []
        
        # 去重
        all_tweets = deduplicate_tweets(all_tweets)
        
        # 按价值排序
        all_tweets.sort(key=lambda t: t.get("value_score", 0), reverse=True)
        
        # 标记已读
        for t in all_tweets:
            if t.get("link"):
                self.state["seen_ids"].append(t["link"])
        self.state["seen_ids"] = self.state["seen_ids"][-500:]  # 保留最近500条
        self.save_state()
        
        # 分类
        hot_tweets = [t for t in all_tweets if t.get("value_score", 0) >= 50]
        normal_tweets = [t for t in all_tweets if 20 <= t.get("value_score", 0) < 50]
        
        # 输出简报
        print("\n" + "=" * 60)
        
        # 🔥 热点内容
        if hot_tweets:
            print("\n🔥 热点内容 (高价值):\n")
            for i, tweet in enumerate(hot_tweets[:3], 1):
                self._print_tweet(tweet, i, detailed=True)
        
        # 📝 常规内容
        print(f"\n{'─' * 60}")
        print(f"📝 今日精选 ({min(len(all_tweets), limit)} 条):\n")
        
        for i, tweet in enumerate(all_tweets[:limit], 1):
            self._print_tweet(tweet, i, detailed=False)
        
        # 总结
        print("\n" + "=" * 60)
        print(f"✓ 共获取 {len(all_tweets)} 条推文")
        if hot_tweets:
            print(f"🔥 发现 {len(hot_tweets)} 条热点内容")
        
        return all_tweets
    
    def _print_tweet(self, tweet, index, detailed=False):
        """打印单条推文"""
        author = tweet.get("author", "unknown")
        author_info = tweet.get("author_info", {})
        text = tweet.get("text", "")
        time_str = tweet.get("time", "")
        score = tweet.get("value_score", 0)
        category = author_info.get("category", "综合")
        
        # 时间
        if time_str:
            try:
                dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                time_str = dt.strftime("%m-%d %H:%M")
            except:
                pass
        
        # 分数标记
        score_mark = ""
        if score >= 70:
            score_mark = " 🔥🔥🔥"
        elif score >= 50:
            score_mark = " 🔥🔥"
        elif score >= 30:
            score_mark = " 🔥"
        
        # 分类标签
        category_emoji = {
            "AI技术": "🤖",
            "AI公司": "🏢",
            "创业投资": "💼",
            "个人成长": "🌱",
            "技术编程": "💻",
            "科技媒体": "📰",
            "投资": "💰",
            "综合": "📌"
        }
        cat_emoji = category_emoji.get(category, "📌")
        
        print(f"{index}. {cat_emoji} [{category}] @{author} · {time_str}{score_mark}")
        
        if detailed:
            # 详细模式：完整翻译
            print(f"   📝 原文:")
            print(f"   {text[:400]}")
            
            if text:
                print(f"\n   🌐 中文:")
                translation = smart_translate(text)
                print(f"   {translation}")
        else:
            # 简洁模式：摘要 + 翻译
            print(f"   📝 {text[:150]}{'...' if len(text) > 150 else ''}")
            
            if text:
                translation = smart_translate(text[:300])
                print(f"   🌐 {translation[:150]}{'...' if len(translation) > 150 else ''}")
        
        print()
    
    def save_report(self, tweets, output_file=None):
        """保存简报"""
        if output_file is None:
            output_file = self.cache_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(tweets, f, ensure_ascii=False, indent=2)
        
        print(f"📁 已保存: {output_file}")
        return output_file

# ==================== CLI ====================

def main():
    if len(sys.argv) < 2:
        print("""
Tech News Pro - 科技资讯聚合器增强版

用法:
  tech_news [选项]

选项:
  --accounts user1,user2  指定账号（逗号分隔）
  --count N               每账号 N 条 (默认 2)
  --limit N               最多显示 N 条 (默认 7)
  --save                  保存到文件
  --list                  列出所有博主
  --full                  完整翻译模式

示例:
  tech_news                           # 默认简报
  tech_news --count 3 --limit 10      # 更多内容
  tech_news --full                    # 完整翻译
  tech_news --accounts karpathy,sama  # 指定博主
""")
        sys.exit(1)
    
    # 解析参数
    accounts = None
    count = 2
    limit = 7
    save = False
    full_mode = False
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--accounts" and i + 1 < len(sys.argv):
            accounts = [a.strip() for a in sys.argv[i + 1].split(",")]
            i += 2
        elif arg == "--count" and i + 1 < len(sys.argv):
            count = int(sys.argv[i + 1])
            i += 2
        elif arg == "--limit" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
            i += 2
        elif arg == "--save":
            save = True
            i += 1
        elif arg == "--full":
            full_mode = True
            i += 1
        elif arg == "--list":
            print("可用博主 (按优先级):\n")
            sorted_accounts = sorted(TECH_ACCOUNTS.items(), 
                                    key=lambda x: x[1].get("priority", 0), 
                                    reverse=True)
            for username, info in sorted_accounts:
                priority = "⭐" * info.get("priority", 0)
                print(f"  @{username:<18} {priority} - {info['desc']}")
            sys.exit(0)
        else:
            i += 1
    
    # 生成简报
    aggregator = TechNewsPro()
    tweets = aggregator.generate_report(accounts, count, limit)
    
    if save and tweets:
        aggregator.save_report(tweets)

if __name__ == "__main__":
    main()
