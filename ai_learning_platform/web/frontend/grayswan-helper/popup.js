// Set status message
function setStatus(message) {
  document.getElementById('status').textContent = message;
  setTimeout(() => {
    document.getElementById('status').textContent = '';
  }, 3000);
}

// Copy prompt from testing interface
document.getElementById('copyPrompt').addEventListener('click', () => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, {action: "copyPrompt"}, (response) => {
      if (response && response.success) {
        setStatus('Prompt copied! Now go to GraySwan platform.');
      } else {
        setStatus('Error: ' + (response ? response.error : 'No response from page'));
      }
    });
  });
});

// Paste prompt to GraySwan platform
document.getElementById('pastePrompt').addEventListener('click', () => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, {action: "pastePrompt"}, (response) => {
      if (response && response.success) {
        setStatus('Prompt pasted to GraySwan!');
      } else {
        setStatus('Error: ' + (response ? response.error : 'No response from page'));
      }
    });
  });
});

// Copy response from GraySwan platform
document.getElementById('copyResponse').addEventListener('click', () => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, {action: "copyResponse"}, (response) => {
      if (response && response.success) {
        setStatus('Response copied! Now go back to testing interface.');
      } else {
        setStatus('Error: ' + (response ? response.error : 'No response from page'));
      }
    });
  });
});

// Paste response to testing interface
document.getElementById('pasteResponse').addEventListener('click', () => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, {action: "pasteResponse"}, (response) => {
      if (response && response.success) {
        setStatus('Response pasted to testing interface!');
      } else {
        setStatus('Error: ' + (response ? response.error : 'No response from page'));
      }
    });
  });
});