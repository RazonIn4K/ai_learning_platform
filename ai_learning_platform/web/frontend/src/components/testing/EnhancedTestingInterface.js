import React, { useState, useEffect } from 'react';
import { getPrompts, createTestResult } from '../../services/api';
import { Box, Typography, TextField, Button, Paper, Grid, Checkbox, FormControlLabel, Radio, RadioGroup, FormControl, FormLabel } from '@mui/material';

function EnhancedTestingInterface() {
  // State variables
  const [category, setCategory] = useState('');
  const [challenge, setChallenge] = useState('');
  const [prompts, setPrompts] = useState([]);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [response, setResponse] = useState('');
  const [modelName, setModelName] = useState('');
  const [success, setSuccess] = useState(true);
  const [notes, setNotes] = useState('');
  const [showGrayswanFrame, setShowGrayswanFrame] = useState(true);
  const [grayswanUrl, setGrayswanUrl] = useState('https://app.grayswan.ai/arena/chat/agent-red-teaming');
  
  // Fetch prompts when category or challenge changes
  useEffect(() => {
    async function fetchPrompts() {
      if (category || challenge) {
        try {
          const fetchedPrompts = await getPrompts({ category, challenge });
          setPrompts(fetchedPrompts);
        } catch (error) {
          alert(`Error fetching prompts: ${error.message}`);
        }
      }
    }
    fetchPrompts();
  }, [category, challenge]);

  // Copy prompt to clipboard and update selected prompt
  const handleCopyPrompt = (prompt) => {
    navigator.clipboard.writeText(prompt.prompt_text);
    setSelectedPrompt(prompt);
    alert('Prompt copied to clipboard! Paste it into the GraySwan platform.');
  };

  // Submit test result
  const handleSubmit = async () => {
    if (!selectedPrompt) {
      alert('Please select a prompt first.');
      return;
    }

    const resultData = {
      prompt_id: selectedPrompt.prompt_id,
      model_name: modelName,
      response: response,
      success: success,
      notes: notes,
      category: selectedPrompt.category,
      challenge_id: selectedPrompt.challenge_id,
      timestamp: new Date().toISOString(),
    };

    try {
      await createTestResult(resultData);
      alert('Result submitted successfully!');
      // Clear form
      setResponse('');
      setModelName('');
      setSuccess(true);
      setNotes('');
      setSelectedPrompt(null);
    } catch (error) {
      alert(`Error submitting result: ${error.message}`);
    }
  };

  // Open GraySwan in a new tab
  const handleOpenGrayswanTab = () => {
    window.open(grayswanUrl, '_blank');
  };

  return (
    <Box className="enhanced-testing-container">
      <Typography variant="h4" gutterBottom>Enhanced Prompt Testing</Typography>
      
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} className="filter-section">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Category"
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              variant="outlined"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Challenge"
              id="challenge"
              value={challenge}
              onChange={(e) => setChallenge(e.target.value)}
              variant="outlined"
            />
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={3} className="two-column-layout">
        <Grid item xs={12} md={5} className="left-column">
          <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Prompts:</Typography>
            <Box className="prompts-list">
              {prompts.map((prompt) => (
                <Paper 
                  key={prompt.prompt_id} 
                  elevation={1} 
                  sx={{ 
                    p: 2, 
                    mb: 2,
                    border: selectedPrompt && selectedPrompt.prompt_id === prompt.prompt_id ? '2px solid #007bff' : 'none',
                    bgcolor: selectedPrompt && selectedPrompt.prompt_id === prompt.prompt_id ? '#f0f7ff' : 'white'
                  }}
                >
                  <Box className="prompt-text" sx={{ mb: 2, maxHeight: '100px', overflowY: 'auto' }}>
                    {prompt.prompt_text}
                  </Box>
                  <Button 
                    variant="contained" 
                    color="primary" 
                    onClick={() => handleCopyPrompt(prompt)}
                    fullWidth
                  >
                    Copy & Test
                  </Button>
                </Paper>
              ))}
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={7} className="right-column">
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Box className="grayswan-controls" sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Button 
                variant="contained" 
                color="secondary" 
                onClick={handleOpenGrayswanTab}
              >
                Open GraySwan in New Tab
              </Button>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={showGrayswanFrame}
                    onChange={(e) => setShowGrayswanFrame(e.target.checked)}
                  />
                }
                label="Show GraySwan Platform"
              />
            </Box>

            {showGrayswanFrame && (
              <Box className="grayswan-frame" sx={{ mb: 3, border: '1px solid #ddd', borderRadius: '4px', p: 1 }}>
                <iframe 
                  src={grayswanUrl} 
                  title="GraySwan Platform"
                  width="100%" 
                  height="500px"
                  sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
                  style={{ border: 'none' }}
                />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block', fontStyle: 'italic' }}>
                  Note: If the iframe doesn't work due to security restrictions, use the "Open in New Tab" button above.
                </Typography>
              </Box>
            )}
          </Paper>

          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Response:</Typography>
            {selectedPrompt && (
              <Box className="selected-prompt-info" sx={{ bgcolor: '#f5f5f5', p: 2, borderRadius: '4px', mb: 3 }}>
                <Typography><strong>Prompt:</strong> {selectedPrompt.prompt_text}</Typography>
                <Typography><strong>Category:</strong> {selectedPrompt.category}</Typography>
                <Typography><strong>Challenge:</strong> {selectedPrompt.challenge_id}</Typography>
              </Box>
            )}

            <Box className="response-form">
              <TextField
                fullWidth
                label="Response"
                id="response"
                value={response}
                onChange={(e) => setResponse(e.target.value)}
                multiline
                rows={8}
                variant="outlined"
                sx={{ mb: 3 }}
              />

              <TextField
                fullWidth
                label="Model Name"
                id="modelName"
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                variant="outlined"
                sx={{ mb: 3 }}
              />

              <FormControl component="fieldset" sx={{ mb: 3 }}>
                <FormLabel component="legend">Success</FormLabel>
                <RadioGroup
                  row
                  name="success"
                  value={success ? 'true' : 'false'}
                  onChange={(e) => setSuccess(e.target.value === 'true')}
                >
                  <FormControlLabel value="true" control={<Radio />} label="True" />
                  <FormControlLabel value="false" control={<Radio />} label="False" />
                </RadioGroup>
              </FormControl>

              <TextField
                fullWidth
                label="Notes"
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                multiline
                rows={4}
                variant="outlined"
                sx={{ mb: 3 }}
              />

              <Button 
                variant="contained" 
                color="primary" 
                onClick={handleSubmit}
                sx={{ mt: 2 }}
              >
                Submit
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default EnhancedTestingInterface;