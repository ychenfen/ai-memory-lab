// Clawd AI Assistant - Content Script
// 注入到所有页面，提供页面级功能

(function() {
  'use strict';
  
  console.log('Clawd AI Assistant content script loaded');
  
  // 工具函数：提取页面内容
  window.extractPageContent = function() {
    return {
      title: document.title,
      url: window.location.href,
      text: document.body.innerText.substring(0, 5000),
      html: document.body.innerHTML.substring(0, 10000)
    };
  };
  
  // 工具函数：提取推特推文
  window.extractTweets = function(count = 10) {
    const tweets = [];
    document.querySelectorAll('article[data-testid="tweet"]').forEach((t, i) => {
      if (i < count) {
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
  };
  
  // 工具函数：高亮元素
  window.highlightElement = function(selector) {
    const element = document.querySelector(selector);
    if (element) {
      element.style.outline = '3px solid #FF4500';
      element.scrollIntoView({ behavior: 'smooth' });
      return true;
    }
    return false;
  };
  
  // 工具函数：自动填充
  window.autoFill = function(data) {
    Object.entries(data).forEach(([selector, value]) => {
      const element = document.querySelector(selector);
      if (element) {
        element.value = value;
        element.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
    return true;
  };
  
})();
