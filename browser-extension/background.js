// Clawd AI Assistant - Background Service Worker

chrome.runtime.onInstalled.addListener(() => {
  console.log('Clawd AI Assistant 已安装');
});

// 点击图标打开侧边栏
chrome.action.onClicked.addListener((tab) => {
  chrome.sidePanel.open({ tabId: tab.id });
});

// 监听来自 content script 的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractTweets') {
    // 处理推文提取
    sendResponse({ success: true });
  }
});

console.log('Clawd AI Assistant background service started');
