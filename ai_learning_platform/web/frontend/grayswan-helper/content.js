// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  try {
    if (request.action === "copyPrompt") {
      // On testing interface - copy the selected prompt
      const promptElement = document.querySelector('.selected .prompt-text');
      if (promptElement) {
        navigator.clipboard.writeText(promptElement.textContent);
        sendResponse({success: true});
      } else {
        sendResponse({success: false, error: "No prompt selected"});
      }
    } else if (request.action === "pastePrompt") {
      // On GraySwan platform - paste into the input field
      const inputField = document.querySelector('textarea[placeholder="Say something..."]');
      if (inputField) {
        navigator.clipboard.readText().then(text => {
          inputField.value = text;
          inputField.dispatchEvent(new Event('input', { bubbles: true }));
          sendResponse({success: true});
        }).catch(err => {
          sendResponse({success: false, error: "Clipboard read error: " + err.message});
        });
        return true; // Keep the message channel open for the async response
      } else {
        sendResponse({success: false, error: "Input field not found"});
      }
    } else if (request.action === "copyResponse") {
      // On GraySwan platform - copy the AI's response
      const responseElements = document.querySelectorAll('.message.ai');
      if (responseElements.length > 0) {
        // Get the last AI response
        const lastResponse = responseElements[responseElements.length - 1];
        const responseText = lastResponse.textContent;
        navigator.clipboard.writeText(responseText);
        sendResponse({success: true});
      } else {
        sendResponse({success: false, error: "No AI response found"});
      }
    } else if (request.action === "pasteResponse") {
      // On testing interface - paste into the response textarea
      const responseField = document.querySelector('#response');
      if (responseField) {
        navigator.clipboard.readText().then(text => {
          responseField.value = text;
          responseField.dispatchEvent(new Event('input', { bubbles: true }));
          sendResponse({success: true});
        }).catch(err => {
          sendResponse({success: false, error: "Clipboard read error: " + err.message});
        });
        return true; // Keep the message channel open for the async response
      } else {
        sendResponse({success: false, error: "Response field not found"});
      }
    }
  } catch (error) {
    sendResponse({success: false, error: error.message});
  }
  return true;
});