// Clawd AI Assistant - Sidepanel Logic

class ClawdAssistant {
  constructor() {
    this.chatContainer = document.getElementById('chat');
    this.userInput = document.getElementById('userInput');
    this.statusDiv = document.getElementById('status');
    this.apiEndpoint = 'http://localhost:18791/api/chat'; // Clawdbot API (GLM port)
    
    this.init();
  }
  
  init() {
    // 绑定按钮事件
    document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
    document.getElementById('extractPage').addEventListener('click', () => this.extractPage());
    document.getElementById('extractTweets').addEventListener('click', () => this.extractTweets());
    document.getElementById('runScript').addEventListener('click', () => this.runCustomScript());
    
    // Enter 发送
    this.userInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    
    this.log('就绪');
  }
  
  log(message) {
    this.statusDiv.textContent = message;
  }
  
  addMessage(text, isUser = false) {
    const msg = document.createElement('div');
    msg.className = `message ${isUser ? 'user' : 'ai'}`;
    msg.innerHTML = text;
    this.chatContainer.appendChild(msg);
    this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
  }
  
  async sendMessage() {
    const text = this.userInput.value.trim();
    if (!text) return;
    
    this.addMessage(text, true);
    this.userInput.value = '';
    this.log('思考中...');
    
    try {
      const response = await this.callAI(text);
      this.addMessage(response);
      this.log('就绪');
    } catch (error) {
      this.addMessage(`❌ 错误: ${error.message}`);
      this.log('错误');
    }
  }
  
  async extractPage() {
    this.log('提取页面内容...');
    
    try {
      // 获取当前标签页
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // 执行脚本提取内容
      const result = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          return {
            title: document.title,
            url: window.location.href,
            text: document.body.innerText.substring(0, 2000),
            html: document.body.innerHTML.substring(0, 5000)
          };
        }
      });
      
      const pageData = result[0].result;
      this.addMessage(`📄 页面提取成功:<br><br>
        <strong>标题:</strong> ${pageData.title}<br>
        <strong>URL:</strong> ${pageData.url}<br>
        <strong>内容:</strong><br>${pageData.text.substring(0, 500)}...
      `);
      
      // 发送给 AI 分析
      this.log('AI 分析中...');
      const analysis = await this.callAI(`分析这个页面:\n\n标题: ${pageData.title}\nURL: ${pageData.url}\n内容: ${pageData.text}`);
      this.addMessage(analysis);
      
    } catch (error) {
      this.addMessage(`❌ 提取失败: ${error.message}`);
    }
    
    this.log('就绪');
  }
  
  async extractTweets() {
    this.log('提取推文...');
    
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // 执行推文提取脚本
      const result = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          const tweets = [];
          document.querySelectorAll('article[data-testid="tweet"]').forEach((t, i) => {
            if (i < 10) {
              const link = t.querySelector('a[href*="/status/"]')?.href || '';
              const id = link.split('/status/')[1]?.split('?')[0] || '';
              const text = t.querySelector('[data-testid="tweetText"]')?.innerText || '';
              const author = t.querySelector('[data-testid="User-Name"] a')?.href?.split('/').pop() || '';
              const time = t.querySelector('time')?.getAttribute('datetime') || '';
              
              if (id && text) {
                tweets.push({ id, text, author, time, link });
              }
            }
          });
          return tweets;
        }
      });
      
      const tweets = result[0].result;
      
      if (tweets.length === 0) {
        this.addMessage('❌ 未找到推文，请确保在推特页面');
      } else {
        let html = `✅ 提取 ${tweets.length} 条推文:<br><br>`;
        tweets.forEach((t, i) => {
          html += `${i + 1}. <strong>@${t.author}</strong><br>${t.text.substring(0, 100)}...<br><br>`;
        });
        this.addMessage(html);
        
        // 发送给 AI 分析
        this.log('AI 分析推文...');
        const analysis = await this.callAI(`分析这些推文:\n\n${JSON.stringify(tweets, null, 2)}`);
        this.addMessage(analysis);
      }
      
    } catch (error) {
      this.addMessage(`❌ 提取失败: ${error.message}`);
    }
    
    this.log('就绪');
  }
  
  async runCustomScript() {
    const script = prompt('输入 JavaScript 代码:');
    if (!script) return;
    
    this.log('执行脚本...');
    
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      const result = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: new Function(script)
      });
      
      const output = result[0].result;
      this.addMessage(`⚡ 执行结果:<br><br><code>${JSON.stringify(output, null, 2)}</code>`);
      
    } catch (error) {
      this.addMessage(`❌ 执行失败: ${error.message}`);
    }
    
    this.log('就绪');
  }
  
  async callAI(message) {
    // 调用 Clawdbot API
    try {
      const response = await fetch(this.apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      
      if (!response.ok) {
        throw new Error('API 请求失败');
      }
      
      const data = await response.json();
      return data.response || data.message || 'AI 返回空响应';
      
    } catch (error) {
      // 如果 API 不可用，返回模拟响应
      return `🤖 (模拟响应) 收到你的消息: "${message.substring(0, 50)}..."<br><br> Clawdbot API 未连接，请确保 Clawdbot 正在运行。`;
    }
  }
}

// 初始化
new ClawdAssistant();
