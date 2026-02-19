#!/usr/bin/env python3
"""
Clawd Extract - 终端版数据提取工具 + GLM AI 分析 + 速率限制 + 缓存

用法:
  clawd-extract.py --url URL --type TYPE [--analyze] [--prompt PROMPT]

功能:
  - 提取页面内容
  - 提取链接
  - 提取图片
  - 自定义选择器
  - GLM AI 分析
  - 本地缓存
  - 速率限制

环境变量:
  GLM_API_KEY - GLM API Key (从 ~/.clawd-glm/clawdbot.json 读取)
"""

import argparse
import json
import sys
import os
import re
import time
import hashlib
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime, timedelta

try:
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    print("⚠️  需要: pip3 install beautifulsoup4 requests")
    sys.exit(1)

class RateLimiter:
    """速率限制器 - 每分钟最多3次调用"""
    def __init__(self, max_calls=3, period=60):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.cache_file = Path.home() / '.clawd-glm' / 'cache' / 'api_calls.json'
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_calls()
    
    def load_calls(self):
        """加载历史调用记录"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file) as f:
                    self.calls = json.load(f)
                # 清理过期记录
                cutoff = time.time() - self.period
                self.calls = [c for c in self.calls if c > cutoff]
            except:
                self.calls = []
    
    def save_calls(self):
        """保存调用记录"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.calls, f)
    
    def wait_if_needed(self):
        """如果需要，等待到可以调用"""
        now = time.time()
        cutoff = now - self.period
        
        # 清理过期记录
        self.calls = [c for c in self.calls if c > cutoff]
        
        if len(self.calls) >= self.max_calls:
            # 需要等待
            oldest = min(self.calls)
            wait_time = oldest + self.period - now
            if wait_time > 0:
                print(f"⏳ 速率限制：等待 {wait_time:.1f} 秒...")
                time.sleep(wait_time)
        
        # 记录本次调用
        self.calls.append(now)
        self.save_calls()

class CacheManager:
    """缓存管理器"""
    def __init__(self):
        self.cache_dir = Path.home() / '.clawd-glm' / 'cache' / 'analysis'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_age_days = 7
    
    def get_cache_key(self, url, data_type, prompt):
        """生成缓存key"""
        content = f"{url}|{data_type}|{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, url, data_type, prompt):
        """获取缓存"""
        key = self.get_cache_key(url, data_type, prompt)
        cache_file = self.cache_dir / f"{key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    cached = json.load(f)
                
                # 检查是否过期
                cached_time = datetime.fromisoformat(cached['timestamp'])
                if datetime.now() - cached_time < timedelta(days=self.max_age_days):
                    print("✅ 使用缓存结果")
                    return cached['analysis']
            except:
                pass
        
        return None
    
    def set(self, url, data_type, prompt, analysis):
        """保存缓存"""
        key = self.get_cache_key(url, data_type, prompt)
        cache_file = self.cache_dir / f"{key}.json"
        
        cached = {
            'url': url,
            'data_type': data_type,
            'prompt': prompt,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cached, f, ensure_ascii=False, indent=2)

class ClawdExtract:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.api_key = self.load_api_key()
        self.api_url = "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions"
        self.rate_limiter = RateLimiter(max_calls=3, period=60)
        self.cache = CacheManager()
    
    def load_api_key(self):
        """从配置文件加载 GLM API Key"""
        config_path = Path.home() / '.clawd-glm' / 'clawdbot.json'
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    return config['models']['providers']['glm']['apiKey']
            except:
                pass
        
        # 从环境变量读取
        return os.getenv('GLM_API_KEY')
    
    def fetch(self, url):
        """获取页面内容"""
        print(f"📡 抓取: {url}")
        try:
            req = Request(url, headers=self.headers)
            with urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            return None
    
    def extract_page(self, url):
        """提取页面内容"""
        html = self.fetch(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除脚本和样式
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        
        return [{
            'title': soup.title.string.strip() if soup.title else '',
            'url': url,
            'text': soup.get_text(separator='\n', strip=True)[:2000]
        }]
    
    def extract_links(self, url):
        """提取所有链接"""
        html = self.fetch(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for a in soup.find_all('a', href=True)[:50]:
            href = a['href']
            if href.startswith('http'):
                links.append({
                    'text': a.get_text(strip=True)[:100] or '[图片/空]',
                    'url': href
                })
        
        return links
    
    def extract_images(self, url):
        """提取所有图片"""
        html = self.fetch(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        images = []
        
        for img in soup.find_all('img', src=True)[:20]:
            src = img['src']
            if src.startswith('http'):
                images.append({
                    'alt': img.get('alt', '[无描述]'),
                    'src': src
                })
        
        return images
    
    def extract_custom(self, url, selector):
        """自定义选择器提取"""
        html = self.fetch(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        selectors = [s.strip() for s in selector.split(',')]
        
        for sel in selectors:
            for tag in soup.select(sel)[:20]:
                results.append({
                    'tag': tag.name,
                    'text': tag.get_text(strip=True)[:200]
                })
        
        return results
    
    def analyze_with_glm(self, data, prompt="分析这些内容", url="", data_type=""):
        """用 GLM 分析提取的数据"""
        if not self.api_key:
            print("⚠️  未配置 GLM API Key")
            return None
        
        # 检查缓存
        cached = self.cache.get(url, data_type, prompt)
        if cached:
            return cached
        
        # 速率限制
        self.rate_limiter.wait_if_needed()
        
        print("🤖 GLM 分析中...")
        
        # 将数据转为文本
        data_text = json.dumps(data, ensure_ascii=False, indent=2)
        
        # 最多重试3次
        for attempt in range(3):
            try:
                response = requests.post(
                    self.api_url,
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'glm-4-flash',
                        'messages': [
                            {
                                'role': 'system',
                                'content': '你是数据分析助手，用简洁的中文分析提取的数据。'
                            },
                            {
                                'role': 'user',
                                'content': f'{prompt}:\n\n{data_text}'
                            }
                        ],
                        'temperature': 0.7
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    analysis = result['choices'][0]['message']['content']
                    
                    # 保存缓存
                    self.cache.set(url, data_type, prompt, analysis)
                    
                    return analysis
                elif response.status_code == 429:
                    # Rate limit - 等待后重试
                    wait_time = (attempt + 1) * 10
                    print(f"⚠️  API 限流，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ API 错误: {response.status_code}")
                    print(f"响应: {response.text}")
                    return None
                    
            except Exception as e:
                print(f"❌ 分析失败: {e}")
                if attempt < 2:
                    print("重试中...")
                    time.sleep(5)
                    continue
                return None
        
        print("❌ 超过最大重试次数")
        return None
    
    def save(self, data, output='json', analysis=None):
        """保存结果"""
        if output == 'json':
            result = {
                'data': data,
                'count': len(data),
                'timestamp': datetime.now().isoformat()
            }
            if analysis:
                result['analysis'] = analysis
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif output == 'csv':
            if not data:
                return
            
            keys = data[0].keys()
            print(','.join(keys))
            for item in data:
                print(','.join(f'"{item.get(k, "")}"' for k in keys))
            
            if analysis:
                print(f"\n\n# GLM 分析:\n{analysis}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='Clawd Extract - 终端版数据提取工具')
    parser.add_argument('--url', required=True, help='目标URL')
    parser.add_argument('--type', choices=['page', 'links', 'images', 'custom'], 
                       default='page', help='提取类型')
    parser.add_argument('--selector', help='自定义选择器（CSS）')
    parser.add_argument('--output', choices=['json', 'csv'], default='json', help='输出格式')
    parser.add_argument('--analyze', action='store_true', help='用 GLM AI 分析')
    parser.add_argument('--prompt', default='分析这些内容，总结关键点', help='分析提示词')
    parser.add_argument('--clear-cache', action='store_true', help='清除缓存')
    
    args = parser.parse_args()
    
    # 清除缓存
    if args.clear_cache:
        cache_dir = Path.home() / '.clawd-glm' / 'cache' / 'analysis'
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
            print("✅ 缓存已清除")
        return
    
    extractor = ClawdExtract()
    
    # 提取数据
    if args.type == 'page':
        data = extractor.extract_page(args.url)
    elif args.type == 'links':
        data = extractor.extract_links(args.url)
    elif args.type == 'images':
        data = extractor.extract_images(args.url)
    elif args.type == 'custom':
        if not args.selector:
            print("❌ custom 类型需要 --selector 参数")
            sys.exit(1)
        data = extractor.extract_custom(args.url, args.selector)
    
    # AI 分析
    analysis = None
    if args.analyze and data:
        analysis = extractor.analyze_with_glm(data, args.prompt, args.url, args.type)
    
    # 保存结果
    extractor.save(data, args.output, analysis)
    
    print(f"\n✅ 提取完成: {len(data)} 条数据", file=sys.stderr)
    if analysis:
        print(f"✅ AI 分析完成", file=sys.stderr)

if __name__ == '__main__':
    main()
