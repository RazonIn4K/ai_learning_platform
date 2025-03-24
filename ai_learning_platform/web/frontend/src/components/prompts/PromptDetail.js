import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
  Typography
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  ContentCopy as CopyIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Science as TestIcon
} from '@mui/icons-material';
import { 
  getPromptById, 
  updatePrompt, 
  deletePrompt, 
  getCategories, 
  getTechniques, 
  getChallenges,
  getTestResults
} from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const PromptDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const isNewPrompt = id === 'new';

  const [prompt, setPrompt] = useState({
    prompt_text: '',
    category: '',
    techniques_used: [],
    challenge_id: '',
    target: '',
    technique: '',
    notes: '',
    status: 'new'
  });
  const [originalPrompt, setOriginalPrompt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [categories, setCategories] = useState([]);
  const [techniques, setTechniques] = useState([]);
  const [challenges, setChallenges] = useState({});
  const [testResults, setTestResults] = useState([]);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(isNewPrompt);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch filter options
        const categoriesData = await getCategories();
        const techniquesData = await getTechniques();
        const challengesData = await getChallenges();
        
        setCategories(categoriesData);
        setTechniques(techniquesData);
        setChallenges(challengesData);
        
        if (!isNewPrompt) {
          // Fetch prompt data
          const promptData = await getPromptById(id);
          setPrompt(promptData);
          setOriginalPrompt(promptData);
          
          // Fetch test results for this prompt
          const resultsData = await getTestResults({ prompt_id: id });
          setTestResults(resultsData);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to load data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, isNewPrompt]);

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setPrompt(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    if (!prompt.prompt_text) {
      setError('Prompt text is required');
      return;
    }
    
    if (!prompt.category) {
      setError('Category is required');
      return;
    }
    
    try {
      setSaving(true);
      setError('');
      
      const updatedPrompt = {
        ...prompt,
        last_updated_timestamp: new Date().toISOString(),
        last_updated_by: currentUser.username
      };
      
      if (isNewPrompt) {
        updatedPrompt.created_by = currentUser.username;
        updatedPrompt.creation_timestamp = new Date().toISOString();
        
        // For new prompts, we need to create it
        // This is a simplified version since we don't have a createPrompt API method
        // In a real implementation, you would call the API to create the prompt
        navigate('/prompts');
      } else {
        // Update existing prompt
        await updatePrompt(id, updatedPrompt);
        setOriginalPrompt(updatedPrompt);
        setIsEditing(false);
      }
    } catch (error) {
      console.error('Error saving prompt:', error);
      setError('Failed to save prompt. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this prompt?')) {
      try {
        await deletePrompt(id);
        navigate('/prompts');
      } catch (error) {
        console.error('Error deleting prompt:', error);
        setError('Failed to delete prompt. Please try again.');
      }
    }
  };

  const handleCopyPrompt = () => {
    navigator.clipboard.writeText(prompt.prompt_text)
      .then(() => {
        alert('Prompt copied to clipboard!');
      })
      .catch(err => {
        console.error('Failed to copy prompt:', err);
        alert('Failed to copy prompt. Please try again.');
      });
  };

  const handleCancel = () => {
    if (isNewPrompt) {
      navigate('/prompts');
    } else {
      setPrompt(originalPrompt);
      setIsEditing(false);
      setError('');
    }
  };

  // Flatten challenges for the dropdown
  const flattenedChallenges = Object.entries(challenges).reduce((acc, [wave, waveItems]) => {
    waveItems.forEach(item => {
      acc.push({ id: item, name: `${wave}: ${item}` });
    });
    return acc;
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Button
          component={RouterLink}
          to="/prompts"
          startIcon={<ArrowBackIcon />}
          sx={{ mr: 2 }}
        >
          Back to Prompts
        </Button>
        <Typography variant="h4" component="h1">
          {isNewPrompt ? 'Create New Prompt' : 'Prompt Details'}
        </Typography>
      </Box>
      
      <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
        {!isNewPrompt && !isEditing && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            <Button
              variant="outlined"
              startIcon={<CopyIcon />}
              onClick={handleCopyPrompt}
              sx={{ mr: 1 }}
            >
              Copy Prompt
            </Button>
            <Button
              variant="outlined"
              startIcon={<TestIcon />}
              component={RouterLink}
              to={`/test?promptId=${id}`}
              sx={{ mr: 1 }}
            >
              Test Prompt
            </Button>
            <Button
              variant="outlined"
              onClick={() => setIsEditing(true)}
            >
              Edit
            </Button>
          </Box>
        )}
        
        {isEditing ? (
          // Edit Mode
          <Box component="form">
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel id="category-label">Category *</InputLabel>
                  <Select
                    labelId="category-label"
                    id="category"
                    name="category"
                    value={prompt.category}
                    label="Category *"
                    onChange={handleInputChange}
                    required
                  >
                    <MenuItem value="">
                      <em>Select a category</em>
                    </MenuItem>
                    {categories.map((category) => (
                      <MenuItem key={category} value={category}>
                        {category}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel id="technique-label">Technique</InputLabel>
                  <Select
                    labelId="technique-label"
                    id="technique"
                    name="technique"
                    value={prompt.technique || ''}
                    label="Technique"
                    onChange={handleInputChange}
                  >
                    <MenuItem value="">
                      <em>Select a technique</em>
                    </MenuItem>
                    {techniques.map((technique) => (
                      <MenuItem key={technique} value={technique}>
                        {technique}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel id="challenge-label">Challenge</InputLabel>
                  <Select
                    labelId="challenge-label"
                    id="challenge_id"
                    name="challenge_id"
                    value={prompt.challenge_id || ''}
                    label="Challenge"
                    onChange={handleInputChange}
                  >
                    <MenuItem value="">
                      <em>Select a challenge</em>
                    </MenuItem>
                    {flattenedChallenges.map((challenge) => (
                      <MenuItem key={challenge.id} value={challenge.id}>
                        {challenge.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel id="status-label">Status</InputLabel>
                  <Select
                    labelId="status-label"
                    id="status"
                    name="status"
                    value={prompt.status || 'new'}
                    label="Status"
                    onChange={handleInputChange}
                  >
                    <MenuItem value="new">New</MenuItem>
                    <MenuItem value="tested">Tested</MenuItem>
                    <MenuItem value="approved">Approved</MenuItem>
                    <MenuItem value="rejected">Rejected</MenuItem>
                  </Select>
                </FormControl>
                
                <TextField
                  fullWidth
                  label="Target"
                  name="target"
                  value={prompt.target || ''}
                  onChange={handleInputChange}
                  sx={{ mb: 3 }}
                />
                
                <TextField
                  fullWidth
                  label="Notes"
                  name="notes"
                  multiline
                  rows={4}
                  value={prompt.notes || ''}
                  onChange={handleInputChange}
                  sx={{ mb: 3 }}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Prompt Text *"
                  name="prompt_text"
                  multiline
                  rows={20}
                  value={prompt.prompt_text}
                  onChange={handleInputChange}
                  required
                  error={!prompt.prompt_text && !!error}
                  sx={{ mb: 3 }}
                />
              </Grid>
            </Grid>
            
            {error && (
              <Typography color="error" sx={{ mt: 2 }}>
                {error}
              </Typography>
            )}
            
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center', gap: 2 }}>
              <Button
                variant="contained"
                color="primary"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Prompt'}
              </Button>
              <Button
                variant="outlined"
                onClick={handleCancel}
              >
                Cancel
              </Button>
              {!isNewPrompt && (
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={handleDelete}
                >
                  Delete
                </Button>
              )}
            </Box>
          </Box>
        ) : (
          // View Mode
          <Box>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Category:
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {prompt.category}
                </Typography>
                
                <Typography variant="subtitle1" gutterBottom>
                  Technique:
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {prompt.technique || 'N/A'}
                </Typography>
                
                <Typography variant="subtitle1" gutterBottom>
                  Challenge:
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {prompt.challenge_id || 'N/A'}
                </Typography>
                
                <Typography variant="subtitle1" gutterBottom>
                  Status:
                </Typography>
                <Chip 
                  label={prompt.status || 'New'} 
                  color={
                    prompt.status === 'tested' ? 'success' :
                    prompt.status === 'approved' ? 'primary' :
                    prompt.status === 'rejected' ? 'error' : 'default'
                  }
                  sx={{ mb: 2 }}
                />
                
                <Typography variant="subtitle1" gutterBottom>
                  Target:
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {prompt.target || 'N/A'}
                </Typography>
                
                <Typography variant="subtitle1" gutterBottom>
                  Notes:
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {prompt.notes || 'N/A'}
                </Typography>
                
                <Typography variant="subtitle1" gutterBottom>
                  Created By:
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {prompt.created_by || 'N/A'} at {new Date(prompt.creation_timestamp).toLocaleString()}
                </Typography>
                
                <Typography variant="subtitle1" gutterBottom>
                  Last Updated:
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {prompt.last_updated_by || 'N/A'} at {new Date(prompt.last_updated_timestamp).toLocaleString()}
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Prompt Text:
                </Typography>
                <Paper 
                  elevation={0} 
                  sx={{ 
                    p: 2, 
                    bgcolor: 'background.default',
                    maxHeight: '500px',
                    overflow: 'auto'
                  }}
                >
                  <Typography 
                    variant="body2" 
                    component="pre"
                    className="prompt-text"
                    sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}
                  >
                    {prompt.prompt_text}
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>
      
      {!isNewPrompt && testResults.length > 0 && (
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Test Results
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          <Grid container spacing={2}>
            {testResults.map((result) => (
              <Grid item xs={12} key={result.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="subtitle1">
                        {result.model_name}
                        <Chip 
                          label={result.success ? 'Success' : 'Failure'} 
                          color={result.success ? 'success' : 'error'}
                          size="small" 
                          sx={{ ml: 1 }}
                        />
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(result.creation_timestamp).toLocaleString()}
                      </Typography>
                    </Box>
                    
                    <Typography 
                      variant="body2" 
                      className="response-text"
                      sx={{ 
                        mb: 2,
                        maxHeight: '100px',
                        overflow: 'auto'
                      }}
                    >
                      {result.response.substring(0, 200)}...
                    </Typography>
                    
                    {result.notes && (
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Notes: {result.notes}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}
    </Box>
  );
};

export default PromptDetail;