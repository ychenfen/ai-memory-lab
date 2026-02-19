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
    document.getElementById('extractLinks').addEventListener('click', () => this.extractLinks());
    document.getElementById('extractImages').addEventListener('click', () => this.extractImages());
    document.getElementById('runScript').addEventListener('click', () => this.runCustomScript());
    document.getElementById('exportJSON').addEventListener('click', () => this.exportJSON());
    document.getElementById('exportCSV').addEventListener('click', () => this.exportCSV());
    document.getElementById('clearChat').addEventListener('click', () => this.clearChat());
    
    // Enter 发送
    this.userInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    
    this.log('就绪');
    this.lastExtractedData = null;
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
  
  async extractLinks() {
    this.log('提取链接...');
    
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      const result = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          const links = [];
          document.querySelectorAll('a').forEach((a, i) => {
            if (i < 50 && a.href && a.href.startsWith('http')) {
              links.push({
                text: a.innerText.trim().substring(0, 100) || '[图片/空]',
                url: a.href
              });
            }
          });
          return links;
        }
      });
      
      const links = result[0].result;
      this.lastExtractedData = links;
      
      let html = `✅ 提取 ${links.length} 个链接:<br><br>`;
      links.slice(0, 10).forEach((l, i) => {
        html += `${i + 1}. <a href="${l.url}" target="_blank">${l.text}</a><br>`;
      });
      if (links.length > 10) html += `<br>... 还有 ${links.length - 10} 个`;
      
      this.addMessage(html);
      
    } catch (error) {
      this.addMessage(`❌ 提取失败: ${error.message}`);
    }
    
    this.log('就绪');
  }
  
  async extractImages() {
    this.log('提取图片...');
    
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      const result = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          const images = [];
          document.querySelectorAll('img').forEach((img, i) => {
            if (i < 20 && img.src && img.src.startsWith('http')) {
              images.push({
                alt: img.alt || '[无描述]',
                src: img.src,
                width: img.naturalWidth,
                height: img.naturalHeight
              });
            }
          });
          return images;
        }
      });
      
      const images = result[0].result;
      this.lastExtractedData = images;
      
      let html = `✅ 提取 ${images.length} 张图片:<br><br>`;
      images.slice(0, 5).forEach((img, i) => {
        html += `${i + 1}. <img src="${img.src}" style="max-width:100%;height:60px;border-radius:4px;margin:4px 0;"><br>${img.alt}<br><br>`;
      });
      
      this.addMessage(html);
      
    } catch (error) {
      this.addMessage(`❌ 提取失败: ${error.message}`);
    }
    
    this.log('就绪');
  }
  
  exportJSON() {
    if (!this.lastExtractedData) {
      this.addMessage('⚠️ 没有数据可导出，请先提取内容');
      return;
    }
    
    const json = JSON.stringify(this.lastExtractedData, null, 2);
    this.downloadFile(json, 'extracted-data.json', 'application/json');
    this.addMessage('✅ 已导出为 JSON 文件');
  }
  
  exportCSV() {
    if (!this.lastExtractedData) {
      this.addMessage('⚠️ 没有数据可导出，请先提取内容');
      return;
    }
    
    const data = this.lastExtractedData;
    if (!Array.isArray(data) || data.length === 0) {
      this.addMessage('⚠️ 数据格式不支持导出CSV');
      return;
    }
    
    const keys = Object.keys(data[0]);
    const csv = [
      keys.join(','),
      ...data.map(row => keys.map(k => `"${row[k] || ''}"`).join(','))
    ].join('\n');
    
    this.downloadFile(csv, 'extracted-data.csv', 'text/csv');
    this.addMessage('✅ 已导出为 CSV 文件');
  }
  
  downloadFile(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }
  
  clearChat() {
    this.chatContainer.innerHTML = `
      <div class="message ai">
        👋 Hi! 我是 Clawd AI 助手。
        <br><br>
        我可以：
        <br>• 分析当前页面
        <br>• 提取推特推文
        <br>• 提取链接和图片
        <br>• 执行自定义脚本
        <br>• 导出数据（JSON/CSV）
      </div>
    `;
    this.lastExtractedData = null;
  }
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
