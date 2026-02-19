# OpenClaw 全栈增强方案

## 目标

将 OpenClaw 从"AI 助手"升级为"全栈 AI 工作站"：
1. ✅ **内置 AI** - 已有（DeepSeek/GLM/Jarvis 多模型协作）
2. 🆕 **浏览器控制** - MCP 协议 + Playwright
3. 🆕 **内置终端** - Shell 访问 + 实时输出

---

## 现有能力

### AI 核心 ✅
- **模型**: GLM-5（主）+ DeepSeek（算法）+ Kimi（长文本）
- **协作**: 三方接力机制（DeepSeek → GLM → Jarvis）
- **通道**: Telegram + iMessage

### 工具能力 ✅
- `exec` - Shell 命令执行（已有终端能力）
- `browser` - 浏览器控制（已有基础）
- `web_search` - 网络搜索
- `web_fetch` - 网页抓取

### MCP 服务器 ✅
- `filesystem` - 文件系统（14 tools）
- `notion` - Notion API（21 tools）
- `github` - GitHub API（26 tools）
- `memory` - 知识图谱（9 tools）
- `context7` - 代码文档（2 tools）

---

## 增强方案

### Phase 1: 浏览器控制增强（1周）

#### 目标
- 真实身份操作网页（绕过反爬）
- 支持复杂交互（登录/点击/填表）
- 截图 + PDF 生成

#### 技术选型
| 方案 | 优势 | 劣势 |
|------|------|------|
| **Playwright** | 功能强、跨浏览器、录制功能 | 需安装浏览器 |
| **Puppeteer** | 轻量、Chrome 专用、已有基础 | 仅 Chrome |

**推荐**: Playwright（功能更强，支持录制）

#### 实施步骤
1. 安装 Playwright
   ```bash
   npm install -g playwright
   playwright install chromium
   ```

2. 创建 MCP 服务器
   ```javascript
   // mcp-browser-server/index.js
   const { chromium } = require('playwright');
   
   server.addTool({
     name: 'browser_navigate',
     description: 'Navigate to URL',
     parameters: { url: 'string' },
     handler: async (params) => {
       const browser = await chromium.launch({ headless: false });
       const page = await browser.newPage();
       await page.goto(params.url);
       return { success: true };
     }
   });
   ```

3. 集成到 OpenClaw
   ```json
   {
     "mcpServers": {
       "browser": {
         "command": "node",
         "args": ["/path/to/mcp-browser-server/index.js"]
       }
     }
   }
   ```

#### 核心能力
- `browser_navigate` - 打开网页
- `browser_click` - 点击元素
- `browser_fill` - 填写表单
- `browser_screenshot` - 截图
- `browser_pdf` - 生成 PDF
- `browser_wait` - 等待元素
- `browser_evaluate` - 执行 JS

---

### Phase 2: 内置终端增强（1周）

#### 目标
- Web 终端 UI（实时输出）
- 多 Shell 会话管理
- 命令历史 + 自动补全

#### 技术选型
| 方案 | 优势 | 劣势 |
|------|------|------|
| **xterm.js** | 专业的终端 UI、功能完整 | 需要前端开发 |
| **原生 exec** | 已有、简单 | 无 UI、无实时输出 |

**推荐**: xterm.js + WebSocket（Web UI）

#### 实施步骤
1. 创建终端服务器
   ```javascript
   // terminal-server/index.js
   const pty = require('node-pty');
   const WebSocket = require('ws');
   
   const wss = new WebSocket.Server({ port: 8080 });
   
   wss.on('connection', (ws) => {
     const shell = pty.spawn('zsh', [], {
       name: 'xterm-256color',
       cwd: process.env.HOME,
       env: process.env
     });
   
     shell.on('data', (data) => ws.send(data));
     ws.on('message', (msg) => shell.write(msg));
   });
   ```

2. 创建 Web UI
   ```html
   <!-- terminal-ui/index.html -->
   <div id="terminal"></div>
   <script src="xterm.js"></script>
   <script>
     const term = new Terminal();
     const socket = new WebSocket('ws://localhost:8080');
     
     term.onData(data => socket.send(data));
     socket.onmessage(msg => term.write(msg.data));
   </script>
   ```

3. 集成到 OpenClaw
   - 添加 `/terminal` 命令打开 Web 终端
   - 保留 `exec` 工具用于脚本执行

---

### Phase 3: 整合优化（1周）

#### 目标
- AI + 浏览器 + 终端联动
- Web UI / PWA 支持
- 文档 + 测试

#### 核心场景
1. **AI 控制浏览器**
   ```
   用户: 帮我抓取这个网页
   AI: 我打开浏览器，导航到网页，截图给你
   [browser_navigate → browser_screenshot]
   ```

2. **AI 操作终端**
   ```
   用户: 运行这个命令
   AI: 我在终端执行命令，实时输出结果
   [exec → streaming output]
   ```

3. **浏览器 + 终端联动**
   ```
   用户: 登录网站并下载数据
   AI: 我用浏览器登录，用终端下载数据
   [browser_fill → exec wget]
   ```

---

## 架构图

```
┌─────────────────────────────────────────┐
│           OpenClaw 全栈工作站            │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │   AI 核心     │  │   Web UI / PWA  │ │
│  │ (DeepSeek/   │  │                 │ │
│  │  GLM/Jarvis) │  │  - 对话界面     │ │
│  └──────┬───────┘  │  - 终端 UI      │ │
│         │          │  - 浏览器预览   │ │
│         ├──────────┴─────────────────┘ │
│         │                               │
│  ┌──────┴───────┐  ┌─────────────────┐ │
│  │ 浏览器控制    │  │   内置终端       │ │
│  │ (Playwright) │  │  (xterm.js)     │ │
│  │              │  │                 │ │
│  │ - 真实身份   │  │  - 多会话       │ │
│  │ - 复杂交互   │  │  - 实时输出     │ │
│  │ - 截图/PDF   │  │  - 历史记录     │ │
│  └──────────────┘  └─────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

---

## 技术栈

### 后端
- **Node.js** - 运行时
- **Playwright** - 浏览器控制
- **node-pty** - 终端模拟
- **WebSocket** - 实时通信

### 前端
- **xterm.js** - 终端 UI
- **React** - UI 框架
- **PWA** - 离线支持

### MCP
- **@modelcontextprotocol/sdk** - MCP SDK
- **自定义 MCP 服务器** - 浏览器/终端

---

## 优先级

### 高优先级（立即实施）
1. ✅ **浏览器控制** - 安装 Playwright，创建 MCP 服务器
2. ✅ **终端 UI** - xterm.js + WebSocket

### 中优先级（1周后）
3. **Web UI** - 整合浏览器 + 终端到统一界面
4. **PWA** - 支持移动端访问

### 低优先级（长期）
5. **Chrome Extension** - 浏览器插件形态
6. **远程控制** - 手机控制 OpenClaw

---

## 时间表

| 周 | 任务 | 交付物 |
|----|------|--------|
| Week 1 | 浏览器控制 | Playwright MCP 服务器 |
| Week 2 | 内置终端 | xterm.js Web 终端 |
| Week 3 | 整合优化 | Web UI / PWA |
| Week 4 | 测试文档 | 文档 + 示例 |

---

## 风险

### 技术风险
- **Playwright 安装** - 需要下载浏览器（约 200MB）
- **WebSocket 稳定性** - 需要处理断线重连
- **性能** - 浏览器 + 终端可能占用较多资源

### 解决方案
- 使用 Docker 隔离环境
- 添加健康检查和自动重连
- 限制并发浏览器/终端数量

---

## 成功指标

1. **浏览器控制**
   - 能打开任意网站
   - 能登录并操作
   - 能截图和生成 PDF

2. **内置终端**
   - 能实时输出命令结果
   - 支持多会话
   - 历史记录可查

3. **整合**
   - AI 能控制浏览器和终端
   - Web UI 统一访问
   - PWA 支持离线

---

## 参考

- [Playwright 文档](https://playwright.dev/)
- [xterm.js 文档](https://xtermjs.org/)
- [MCP 协议](https://modelcontextprotocol.io/)
- [Claude Code 浏览器插件](https://github.com/anthropics/claude-code)

---

*方案设计于 2026-02-19 16:35 GMT+8*
