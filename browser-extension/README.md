# Clawd AI Assistant - 浏览器内置 AI 助手

## 🎯 功能

- **侧边栏 AI 对话** - 在任何页面打开 AI 助手
- **页面分析** - 一键提取页面内容，AI 自动分析
- **推特爬虫** - 自动提取推特推文，AI 分析热点
- **脚本执行** - 在页面中执行自定义 JavaScript
- **自动填充** - 自动填充表单（开发中）

## 📦 安装

### 1. 加载插件

1. 打开 Chrome，访问 `chrome://extensions/`
2. 开启"开发者模式"（右上角）
3. 点击"加载已解压的扩展程序"
4. 选择 `browser-extension` 文件夹

### 2. 启动 Clawdbot API

```bash
cd ~/clawd-glm
clawdbot gateway start
```

Clawdbot 会在 `http://localhost:3000` 提供 API。

### 3. 使用

1. 点击浏览器工具栏的 Clawd AI 图标
2. 侧边栏会打开
3. 点击按钮或输入消息与 AI 交互

## 🚀 使用场景

### 场景1：分析网页

1. 打开任意网页
2. 点击"📄 提取页面"
3. AI 自动分析内容并给出见解

### 场景2：爬取推特

1. 打开推特页面（如 twitter.com/karpathy）
2. 点击"🐦 提取推文"
3. AI 自动提取前 10 条推文并分析

### 场景3：执行脚本

1. 点击"⚡ 执行脚本"
2. 输入 JavaScript 代码（如 `document.title`）
3. 查看执行结果

## 🛠️ 高级功能

### 自定义 API 端点

修改 `sidepanel.js` 中的 `apiEndpoint`：

```javascript
this.apiEndpoint = 'http://your-api-endpoint';
```

### 添加新功能

在 `sidepanel.js` 中添加新按钮：

```javascript
// 添加按钮
<button class="action-btn" id="newFeature">🔧 新功能</button>

// 添加事件
document.getElementById('newFeature').addEventListener('click', () => this.newFeature());

// 实现方法
async newFeature() {
  // 你的代码
}
```

## 📋 文件结构

```
browser-extension/
├── manifest.json        # 插件配置
├── sidepanel.html       # 侧边栏 UI
├── sidepanel.js         # 侧边栏逻辑
├── background.js        # 后台服务
├── content.js           # 页面脚本
└── README.md            # 说明文档
```

## 🔧 开发计划

- [ ] 多 AI 模型切换（Claude/GPT/GLM）
- [ ] 历史对话记录
- [ ] 自定义快捷键
- [ ] 自动化工作流
- [ ] 与 Clawdbot 深度集成

## ⚙️ 配置

### Clawdbot API

插件需要 Clawdbot 运行。检查状态：

```bash
clawdbot gateway status
```

如果未运行：

```bash
clawdbot gateway start
```

### API Endpoint

当前配置：`http://localhost:18791`

如果你的 Clawdbot 使用不同端口，修改 `sidepanel.js`：

```javascript
this.apiEndpoint = 'http://your-port/api/chat';
```

### 离线模式

如果 Clawdbot 未运行，插件会以"演示模式"工作：
- ✅ 页面提取 - 完全可用
- ✅ 推特爬虫 - 完全可用
- ✅ 脚本执行 - 完全可用
- ⚠️  AI 对话 - 返回模拟响应

## 📝 注意事项

- 首次使用推荐先测试"页面提取"和"推特爬虫"功能
- 推文提取只在 twitter.com 有效
- 页面内容最多提取 5000 字符

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**Created by GLM + Clawdbot Team** 🤖
