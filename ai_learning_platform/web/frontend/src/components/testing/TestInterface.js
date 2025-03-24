import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  FormControl,
  FormControlLabel,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Radio,
  RadioGroup,
  Select,
  TextField,
  Typography
} from '@mui/material';
import { ContentCopy as CopyIcon } from '@mui/icons-material';
import { 
  getPromptById, 
  getPrompts, 
  getModels, 
  createTestResult 
} from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const TestInterface = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const queryParams = new URLSearchParams(location.search);
  const promptIdFromUrl = queryParams.get('promptId');

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [prompts, setPrompts] = useState([]);
  const [models, setModels] = useState([]);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [selectedPromptId, setSelectedPromptId] = useState(promptIdFromUrl || '');
  const [selectedModel, setSelectedModel] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [success, setSuccess] = useState(false);
  const [successScore, setSuccessScore] = useState(0.5);
  const [notes, setNotes] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch prompts
        const promptsData = await getPrompts({ limit: 100 });
        setPrompts(promptsData);
        
        // Fetch models
        const modelsData = await getModels();
        setModels(modelsData);
        
        // If promptId is provided in URL, load that prompt
        if (promptIdFromUrl) {
          const promptData = await getPromptById(promptIdFromUrl);
          setSelectedPrompt(promptData);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to load data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [promptIdFromUrl]);

  const handlePromptChange = async (event) => {
    const promptId = event.target.value;
    setSelectedPromptId(promptId);
    setError('');
    
    if (!promptId) {
      setSelectedPrompt(null);
      return;
    }
    
    try {
      setLoading(true);
      const promptData = await getPromptById(promptId);
      setSelectedPrompt(promptData);
    } catch (error) {
      console.error('Error fetching prompt:', error);
      setError('Failed to load prompt. Please try again.');
      setSelectedPrompt(null);
    } finally {
      setLoading(false);
    }
  };

  const handleModelChange = (event) => {
    setSelectedModel(event.target.value);
  };

  const handleCopyPrompt = () => {
    if (!selectedPrompt) return;
    
    navigator.clipboard.writeText(selectedPrompt.prompt_text)
      .then(() => {
        alert('Prompt copied to clipboard!');
      })
      .catch(err => {
        console.error('Failed to copy prompt:', err);
        alert('Failed to copy prompt. Please try again.');
      });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!selectedPromptId) {
      setError('Please select a prompt');
      return;
    }
    
    if (!selectedModel) {
      setError('Please select an AI model');
      return;
    }
    
    if (!aiResponse) {
      setError('Please enter the AI response');
      return;
    }
    
    try {
      setSubmitting(true);
      setError('');
      
      const resultData = {
        prompt_id: selectedPromptId,
        model_name: selectedModel,
        model_provider: 'gray_swan_agent',
        response: aiResponse,
        success: success,
        success_score: parseFloat(successScore),
        notes: notes,
        category: selectedPrompt?.category,
        challenge_id: selectedPrompt?.challenge_id
      };
      
      await createTestResult(resultData);
      
      // Reset form
      setAiResponse('');
      setSuccess(false);
      setSuccessScore(0.5);
      setNotes('');
      
      // Navigate to results page
      navigate('/results');
    } catch (error) {
      console.error('Error submitting test result:', error);
      setError('Failed to submit test result. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Manual Testing Interface
      </Typography>
      
      <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Step 1: Select a Prompt and Model
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth error={!selectedPromptId && !!error}>
              <InputLabel id="prompt-select-label">Select Prompt</InputLabel>
              <Select
                labelId="prompt-select-label"
                id="prompt-select"
                value={selectedPromptId}
                label="Select Prompt"
                onChange={handlePromptChange}
              >
                <MenuItem value="">
                  <em>Select a prompt</em>
                </MenuItem>
                {prompts.map((prompt) => (
                  <MenuItem key={prompt.id} value={prompt.id}>
                    {prompt.category} - {prompt.technique || 'N/A'} - {prompt.prompt_text.substring(0, 50)}...
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth error={!selectedModel && !!error}>
              <InputLabel id="model-select-label">Select AI Model</InputLabel>
              <Select
                labelId="model-select-label"
                id="model-select"
                value={selectedModel}
                label="Select AI Model"
                onChange={handleModelChange}
              >
                <MenuItem value="">
                  <em>Select an AI model</em>
                </MenuItem>
                {models.map((model) => (
                  <MenuItem key={model} value={model}>
                    {model}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>
      
      {selectedPrompt && (
        <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Step 2: Copy and Test the Prompt
            </Typography>
            <Button 
              variant="outlined" 
              startIcon={<CopyIcon />}
              onClick={handleCopyPrompt}
            >
              Copy Prompt
            </Button>
          </Box>
          
          <Card sx={{ mb: 3, position: 'relative' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Category: {selectedPrompt.category}
                {selectedPrompt.technique && ` | Technique: ${selectedPrompt.technique}`}
                {selectedPrompt.challenge_id && ` | Challenge: ${selectedPrompt.challenge_id}`}
              </Typography>
              
              <Divider sx={{ mb: 2 }} />
              
              <Typography 
                variant="body2" 
                component="pre"
                className="prompt-text"
                sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}
              >
                {selectedPrompt.prompt_text}
              </Typography>
            </CardContent>
          </Card>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            1. Copy the prompt above
            2. Paste it to the AI model ({selectedModel || "selected model"})
            3. Get the response
            4. Paste the response below
          </Typography>
        </Paper>
      )}
      
      <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Step 3: Record the Response
        </Typography>
        
        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            label="AI Response"
            multiline
            rows={8}
            fullWidth
            value={aiResponse}
            onChange={(e) => setAiResponse(e.target.value)}
            placeholder="Paste the AI's response here..."
            sx={{ mb: 3 }}
            error={!aiResponse && !!error}
          />
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl component="fieldset" sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Was the test successful?
                </Typography>
                <RadioGroup
                  row
                  value={success}
                  onChange={(e) => setSuccess(e.target.value === 'true')}
                >
                  <FormControlLabel value={true} control={<Radio />} label="Success" />
                  <FormControlLabel value={false} control={<Radio />} label="Failure" />
                </RadioGroup>
              </FormControl>
              
              <FormControl fullWidth sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Success Score (0-1)
                </Typography>
                <TextField
                  type="number"
                  value={successScore}
                  onChange={(e) => setSuccessScore(e.target.value)}
                  inputProps={{ min: 0, max: 1, step: 0.1 }}
                />
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                label="Notes"
                multiline
                rows={5}
                fullWidth
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add any notes or observations about the test..."
              />
            </Grid>
          </Grid>
          
          {error && (
            <Typography color="error" sx={{ mt: 2 }}>
              {error}
            </Typography>
          )}
          
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={submitting || !selectedPromptId || !selectedModel || !aiResponse}
            >
              {submitting ? 'Submitting...' : 'Submit Test Result'}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default TestInterface;