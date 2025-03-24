// Listen for messages from popup or background script
browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Content script received message:', request);
  
  // Handle different actions
  switch (request.action) {
    case 'fetchPrompts':
      return handleFetchPrompts(request.data, sendResponse);
    
    case 'submitPrompt':
      return handleSubmitPrompt(request.data, sendResponse);
    
    case 'getResponse':
      return handleGetResponse(sendResponse);
    
    case 'submitResult':
      return handleSubmitResult(request.data, sendResponse);
    
    default:
      sendResponse({ success: false, error: 'Unknown action' });
      return false;
  }
});

// Handle fetching prompts from testing platform
function handleFetchPrompts(data, sendResponse) {
  const { category, challenge, maxPrompts } = data;
  
  // Check if we're on the testing platform
  if (!window.location.href.includes('localhost:3000')) {
    sendResponse({ success: false, error: 'Not on testing platform' });
    return false;
  }
  
  try {
    // Find category and challenge inputs
    const categoryInput = document.getElementById('category');
    const challengeInput = document.getElementById('challenge');
    
    if (!categoryInput || !challengeInput) {
      sendResponse({ success: false, error: 'Could not find input fields' });
      return false;
    }
    
    // Set values and trigger change events
    categoryInput.value = category;
    challengeInput.value = challenge;
    
    categoryInput.dispatchEvent(new Event('input', { bubbles: true }));
    challengeInput.dispatchEvent(new Event('input', { bubbles: true }));
    
    // Wait for prompts to load
    setTimeout(() => {
      // Get all prompt elements
      const promptElements = document.querySelectorAll('li');
      let prompts = [];
      
      // Extract prompt data
      promptElements.forEach(element => {
        const promptText = element.querySelector('.prompt-text')?.textContent || 
                          element.textContent.split('Copy')[0].trim();
        
        if (promptText) {
          // Generate a unique ID if not available
          const promptId = element.dataset.promptId || 
                          `prompt-${Math.random().toString(36).substring(2, 10)}`;
          
          prompts.push({
            prompt_id: promptId,
            prompt_text: promptText,
            category: category,
            challenge_id: challenge
          });
        }
      });
      
      // Limit number of prompts if needed
      if (maxPrompts && prompts.length > maxPrompts) {
        prompts = prompts.slice(0, maxPrompts);
      }
      
      sendResponse({ success: true, prompts });
    }, 2000);
    
    return true; // Keep the message channel open for async response
  } catch (error) {
    sendResponse({ success: false, error: error.message });
    return false;
  }
}

// Handle submitting a prompt to GraySwan
function handleSubmitPrompt(data, sendResponse) {
  const { prompt } = data;
  
  // Check if we're on GraySwan platform
  if (!window.location.href.includes('app.grayswan.ai/arena/chat/agent-red-teaming')) {
    sendResponse({ success: false, error: 'Not on GraySwan platform' });
    return false;
  }
  
  try {
    // Check if we need to start a new chat
    const newChatButton = document.querySelector('button[aria-label="New chat"]');
    if (newChatButton) {
      newChatButton.click();
      
      // Wait for the input field to be ready
      setTimeout(() => {
        submitPromptToGraySwan(prompt, sendResponse);
      }, 1000);
    } else {
      submitPromptToGraySwan(prompt, sendResponse);
    }
    
    return true; // Keep the message channel open for async response
  } catch (error) {
    sendResponse({ success: false, error: error.message });
    return false;
  }
}

// Helper function to submit prompt to GraySwan
function submitPromptToGraySwan(prompt, sendResponse) {
  // Find the input field
  const inputField = document.querySelector('textarea[placeholder="Say something..."]');
  
  if (!inputField) {
    sendResponse({ success: false, error: 'Could not find input field' });
    return;
  }
  
  // Set the prompt text
  inputField.value = prompt;
  inputField.dispatchEvent(new Event('input', { bubbles: true }));
  
  // Find and click the send button
  const sendButton = document.querySelector('button[aria-label="Send message"]') || 
                    document.querySelector('button[type="submit"]');
  
  if (!sendButton) {
    sendResponse({ success: false, error: 'Could not find send button' });
    return;
  }
  
  sendButton.click();
  sendResponse({ success: true });
}

// Handle getting response from GraySwan
function handleGetResponse(sendResponse) {
  // Check if we're on GraySwan platform
  if (!window.location.href.includes('app.grayswan.ai/arena/chat/agent-red-teaming')) {
    sendResponse({ success: false, error: 'Not on GraySwan platform' });
    return false;
  }
  
  try {
    // Find all AI response elements
    const responseElements = document.querySelectorAll('.message.ai');
    
    if (responseElements.length === 0) {
      sendResponse({ success: false, error: 'No AI responses found' });
      return false;
    }
    
    // Get the last response
    const lastResponse = responseElements[responseElements.length - 1];
    const responseText = lastResponse.textContent.trim();
    
    sendResponse({ success: true, response: responseText });
    return false;
  } catch (error) {
    sendResponse({ success: false, error: error.message });
    return false;
  }
}

// Handle submitting result to testing platform
function handleSubmitResult(data, sendResponse) {
  const { promptId, response, modelName, success, notes } = data;
  
  // Check if we're on the testing platform
  if (!window.location.href.includes('localhost:3000')) {
    sendResponse({ success: false, error: 'Not on testing platform' });
    return false;
  }
  
  try {
    // Find the prompt with the matching ID or text
    const promptElements = document.querySelectorAll('li');
    let targetPrompt = null;
    
    for (const element of promptElements) {
      if (element.dataset.promptId === promptId || 
          element.textContent.includes(promptId)) {
        targetPrompt = element;
        break;
      }
    }
    
    if (!targetPrompt) {
      sendResponse({ success: false, error: 'Could not find matching prompt' });
      return false;
    }
    
    // Click the prompt to select it
    const copyButton = targetPrompt.querySelector('button');
    if (copyButton) {
      copyButton.click();
    } else {
      targetPrompt.click();
    }
    
    // Fill in the response form
    setTimeout(() => {
      // Find form fields
      const responseField = document.getElementById('response');
      const modelNameField = document.getElementById('modelName');
      const successTrueRadio = document.getElementById('success-true');
      const successFalseRadio = document.getElementById('success-false');
      const notesField = document.getElementById('notes');
      
      if (!responseField || !modelNameField || 
          !successTrueRadio || !successFalseRadio || !notesField) {
        sendResponse({ success: false, error: 'Could not find form fields' });
        return;
      }
      
      // Fill in the fields
      responseField.value = response;
      modelNameField.value = modelName;
      
      if (success) {
        successTrueRadio.checked = true;
      } else {
        successFalseRadio.checked = true;
      }
      
      notesField.value = notes;
      
      // Trigger input events
      responseField.dispatchEvent(new Event('input', { bubbles: true }));
      modelNameField.dispatchEvent(new Event('input', { bubbles: true }));
      successTrueRadio.dispatchEvent(new Event('change', { bubbles: true }));
      successFalseRadio.dispatchEvent(new Event('change', { bubbles: true }));
      notesField.dispatchEvent(new Event('input', { bubbles: true }));
      
      // Submit the form
      const submitButton = document.querySelector('button[type="submit"]') || 
                          document.querySelector('button');
      
      if (submitButton) {
        submitButton.click();
        sendResponse({ success: true });
      } else {
        sendResponse({ success: false, error: 'Could not find submit button' });
      }
    }, 1000);
    
    return true; // Keep the message channel open for async response
  } catch (error) {
    sendResponse({ success: false, error: error.message });
    return false;
  }
}