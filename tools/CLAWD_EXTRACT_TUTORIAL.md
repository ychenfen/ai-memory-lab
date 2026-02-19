# Clawd Extract - 完整使用教程

## 📦 工具位置

```bash
~/clawd-glm/tools/clawd-extract.py
```

---

## 🚀 快速开始

### 1. 基础提取（无AI）

```bash
# 提取链接
python3 ~/clawd-glm/tools/clawd-extract.py \
  --url https://news.ycombinator.com \
  --type links

# 提取图片
python3 ~/clawd-glm/tools/clawd-extract.py \
  --url https://news.ycombinator.com \
  --type images

# 提取页面内容
python3 ~/clawd-glm/tools/clawd-extract.py \
  --url https://news.ycombinator.com \
  --type page
```

---

### 2. AI 分析模式

```bash
# 提取链接 + AI分析
python3 ~/clawd-glm/tools/clawd-extract.py \
  --url https://news.ycombinator.com \
  --type links \
  --analyze

# 自定义分析提示
python3 ~/clawd-glm/tools/clawd-extract.py \
  --url https://news.ycombinator.com \
  --type links \
  --analyze \
  --prompt "总结最重要的3个链接"
```

---

## 📝 参数说明

| 参数 | 说明 | 示例 |
|-----|------|------|
| `--url` | 目标网址 | `https://example.com` |
| `--type` | 提取类型 | `page` / `links` / `images` / `custom` |
| `--analyze` | 启用AI分析 | 无需参数 |
| `--prompt` | AI分析提示词 | `"总结重点"` |
| `--output` | 输出格式 | `json` / `csv` |
| `--selector` | 自定义选择器 | `"h1,h2,h3"` |
| `--clear-cache` | 清除缓存 | 无需参数 |

---

## 🎯 实用场景

### 场景1：提取科技新闻

```bash
python3 ~/clawd-glm/tools/clawd-extract.py \
  --url https://news.ycombinator.com \
  --type links \
  --analyze \
  --prompt "总结前5个最重要的科技新闻" \
  --output json > news.json
```

**结果**：
- 提取50个链接
- AI分析前5个重要新闻
- 保存为JSON文件

---

### 场景2：提取推特内容

```bash
python3 ~/clawd-glm/tools/clawd-extract.py \
  --url https://twitter.com/karpathy \
  --type custom \
  --selector '[data-testid="tweet"]' \
  --analyze \
  --prompt "总结这些推文的主要观点"
```

**结果**：
- 提取推文内容
- AI总结主要观点

---

### 场景3：批量提取产品信息

```bash
# 创建批量脚本
cat > extract_products.sh << 'EOF'
#!/bin/bash
URLS=(
  "https://product1.com"
  "https://product2.com"
  "https://product3.com"
)

for url in "${URLS[@]}"; do
  echo "提取: $url"
  python3 ~/clawd-glm/tools/clawd-extract.py \
    --url "$url" \
    --type custom \
    --selector ".product-name, .price" \
    --output json >> products.json
done
EOF

chmod +x extract_products.sh
./extract_products.sh
```

---

## 🔧 高级功能

### 1. 速率限制

**内置保护**：
- 每分钟最多3次API调用
- 自动等待（显示剩余时间）
- 调用记录持久化

**手动检查**：
```bash
# 查看调用记录
cat ~/.clawd-glm/cache/api_calls.json
```

---

### 2. 本地缓存

**自动缓存**：
- 相同URL+类型+提示词缓存7天
- 避免重复API调用
- 节省配额

**清除缓存**：
```bash
python3 ~/clawd-glm/tools/clawd-extract.py --clear-cache
```

**查看缓存**：
```bash
ls ~/.clawd-glm/cache/analysis/
```

---

### 3. 导出格式

**JSON（默认）**：
```bash
python3 ~/clawd-glm/tools/clawd-extract.py \
  --url https://example.com \
  --type links \
  --output json
```

**CSV（Excel可打开）**：
```bash
python3 ~/clawd-glm/tools/clawd-extract.py \
  --url https://example.com \
  --type links \
  --output csv > links.csv
```

---

## 💡 快捷命令

### 添加别名

编辑 `~/.zshrc`：

```bash
# Clawd Extract 快捷命令
alias extract-links='python3 ~/clawd-glm/tools/clawd-extract.py --type links'
alias extract-images='python3 ~/clawd-glm/tools/clawd-extract.py --type images'
alias extract-page='python3 ~/clawd-glm/tools/clawd-extract.py --type page'
alias extract-analyze='python3 ~/clawd-glm/tools/clawd-extract.py --analyze'
```

重新加载：
```bash
source ~/.zshrc
```

### 使用别名

```bash
# 提取链接
extract-links --url https://news.ycombinator.com

# 提取并分析
extract-analyze --url https://news.ycombinator.com --type links --prompt "总结重点"
```

---

## 📊 性能优化

### 1. 减少API调用

**使用缓存**：
- 第一次：调用API（耗时5-10秒）
- 后续：使用缓存（即时返回）

**批量处理**：
- 一次提取多个数据
- 一次AI分析总结

---

### 2. 优化选择器

**性能对比**：
```bash
# 慢（通用选择器）
--selector "*"

# 快（精确选择器）
--selector "article h1, article .summary"
```

---

## 🐛 故障排查

### 问题1：429 限流

**原因**：API调用频率过高

**解决**：
- 等待1分钟
- 工具自动重试（10秒间隔）
- 使用缓存（避免重复调用）

---

### 问题2：抓取失败

**原因**：网站反爬虫

**解决**：
- 更换User-Agent（修改代码）
- 添加延时（多次请求）
- 使用代理

---

### 问题3：提取为空

**原因**：选择器错误

**解决**：
- 检查网站HTML结构
- 使用浏览器开发者工具
- 测试选择器

---

## 📈 使用统计

### 查看统计

```bash
# API调用次数
wc -l ~/.clawd-glm/cache/api_calls.json

# 缓存文件数
ls ~/.clawd-glm/cache/analysis/ | wc -l

# 缓存总大小
du -sh ~/.clawd-glm/cache/
```

---

## 🎓 最佳实践

1. **先用无AI模式测试** - 确认数据正确
2. **添加AI分析** - 验证分析结果
3. **使用缓存** - 避免重复调用
4. **批量处理** - 一次提取多个数据
5. **导出备份** - 定期保存结果

---

## 📚 更多示例

### GitHub 仓库分析

```bash
python3 ~/clawd-glm/tools/clawd-extract.py \
  --url https://github.com/clawdbot/clawdbot \
  --type custom \
  --selector "h1, .f4" \
  --analyze \
  --prompt "总结这个项目的核心功能"
```

---

### 博客文章总结

```bash
python3 ~/clawd-glm/tools/clawd-extract.py \
  --url https://blog.example.com/article \
  --type page \
  --analyze \
  --prompt "用3个要点总结这篇文章"
```

---

## 🆘 获取帮助

```bash
# 查看帮助
python3 ~/clawd-glm/tools/clawd-extract.py --help

# 清除缓存
python3 ~/clawd-glm/tools/clawd-extract.py --clear-cache
```

---

**现在就开始使用吧！** 🚀
