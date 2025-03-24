// Enhanced background.js with better error handling and retry mechanism
const API_BASE_URL = 'http://localhost:5000/api';
const MAX_RETRIES = 3;
const INITIAL_RETRY_DELAY = 1000; // ms

// Function to make API requests with retry
async function makeApiRequest(url, options, retries = 0) {
  try {
    console.log(`Making API request to ${url}`);
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`API error: ${response.status} ${response.statusText} - ${errorData.error || 'Unknown error'}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API request failed: ${error.message}`);
    
    // Retry logic with exponential backoff
    if (retries < MAX_RETRIES) {
      const delay = INITIAL_RETRY_DELAY * Math.pow(2, retries);
      console.log(`Retrying (${retries + 1}/${MAX_RETRIES}) after ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
      return makeApiRequest(url, options, retries + 1);
    }
    
    throw error;
  }
}

// Connection status tracking
let isConnected = false;
let connectionCheckInterval;

// Function to check API connection
async function checkApiConnection() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const wasConnected = isConnected;
    isConnected = response.ok;
    
    // If connection status changed, notify UI
    if (wasConnected !== isConnected) {
      browser.runtime.sendMessage({
        action: 'connectionStatusChanged',
        isConnected
      }).catch(() => {});
    }
  } catch (error) {
    if (isConnected) {
      isConnected = false;
      browser.runtime.sendMessage({
        action: 'connectionStatusChanged',
        isConnected: false
      }).catch(() => {});
    }
  }
}

// Start connection checking when extension loads
function startConnectionChecking() {
  checkApiConnection();
  connectionCheckInterval = setInterval(checkApiConnection, 10000); // Check every 10 seconds
}

// Stop connection checking
function stopConnectionChecking() {
  if (connectionCheckInterval) {
    clearInterval(connectionCheckInterval);
  }
}

// Initialize connection checking
startConnectionChecking();

// Enhanced message handling
browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background script received message:', request);

  switch (request.action) {
    case 'getTemplates':
      if (!isConnected) {
        sendResponse({
          success: false,
          error: 'API server is not available. Please check if the server is running.'
        });
        return false;
      }
      
      makeApiRequest(`${API_BASE_URL}/templates`)
        .then(data => {
          sendResponse({ success: true, templates: data.templates || [] });
        })
        .catch(error => {
          console.error('Error fetching templates:', error);
          sendResponse({
            success: false,
            error: 'Failed to fetch templates. Please check if the API server is running.',
            details: error.message
          });
        });
      return true; // Keep the message channel open for async response
      
      case 'getSuccessfulPrompts':
        if (!isConnected) {
          sendResponse({
            success: false,
            error: 'API server is not available. Please check if the server is running.'
          });
          return false;
        }
        
        makeApiRequest(`${API_BASE_URL}/successful-prompts?challenge=${encodeURIComponent(request.data.challenge)}`)
          .then(data => {
            sendResponse({ success: true, prompts: data.prompts || [] });
          })
          .catch(error => {
            console.error('Error fetching successful prompts:', error);
            sendResponse({
              success: false,
              error: 'Failed to fetch successful prompts. Please check if the API server is running.',
              details: error.message
            });
          });
        return true;
    
    case 'analyzePrompts':
      if (!isConnected) {
        sendResponse({
          success: false,
          error: 'API server is not available. Please check if the server is running.'
        });
        return false;
      }
        
      makeApiRequest(`${API_BASE_URL}/analyze-prompts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          challenge: request.data.challenge
        })
      })
        .then(data => {
          sendResponse({ success: true, analysis: data });
        })
        .catch(error => {
          console.error('Error analyzing prompts:', error);
          sendResponse({
            success: false,
            error: 'Failed to analyze prompts. Please check if the API server is running.',
            details: error.message
          });
        });
      return true;
        
      case 'generatePrompts':
        if (!isConnected) {
          sendResponse({
            success: false,
            error: 'API server is not available. Please check if the server is running.'
          });
          return false;
        }
        
        makeApiRequest(`${API_BASE_URL}/generate-prompts`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            challenge: request.data.challenge,
            count: request.data.count,
            template: request.data.template
          })
        })
          .then(data => {
            sendResponse({ success: true, prompts: data.prompts || [] });
          })
          .catch(error => {
            console.error('Error generating prompts:', error);
            sendResponse({
              success: false,
              error: 'Failed to generate prompts. Please check if the API server is running.',
              details: error.message
            });
          });
        return true;
    
    // Other cases with similar improvements...
    case 'getChallenges':
      // For simplicity, we're storing challenge data in extension storage
      browser.storage.local.get('challenges').then(data => {
        sendResponse({ success: true, challenges: data.challenges || {} });
      });
      return true; // Keep the message channel open for async response

    case 'updateChallenge':
      browser.storage.local.get('challenges').then(data => {
        let challenges = data.challenges || {};
        challenges[request.data.challenge] = request.data.status;
        browser.storage.local.set({ challenges }).then(() => {
          sendResponse({ success: true });
        });
      });
      return true; // Keep the message channel open for async response
      
    case 'checkConnection':
      checkApiConnection().then(() => {
        sendResponse({ isConnected });
      });
      return true;
      
    default:
      sendResponse({ success: false, error: 'Unknown action' });
      return false;
  }
});

// Clean up when extension is unloaded
browser.runtime.onSuspend.addListener(() => {
  stopConnectionChecking();
});