// Global state
let isAutomationRunning = false;

// Listen for messages from popup or content scripts
browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background script received message:', request);
  
  switch (request.action) {
    case 'startAutomation':
      isAutomationRunning = true;
      sendResponse({ success: true });
      break;
    
    case 'stopAutomation':
      isAutomationRunning = false;
      sendResponse({ success: true });
      break;
    
    case 'getAutomationStatus':
      sendResponse({ isRunning: isAutomationRunning });
      break;
    
    default:
      sendResponse({ success: false, error: 'Unknown action' });
  }
});

// Create placeholder icons directory and files
browser.runtime.onInstalled.addListener(() => {
  console.log('Extension installed');
});