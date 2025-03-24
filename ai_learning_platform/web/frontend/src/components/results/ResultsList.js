import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
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
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Typography,
  Pagination
} from '@mui/material';
import { getTestResults, getModels, getCategories, getPrompts } from '../../services/api';

const ResultsList = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [models, setModels] = useState([]);
  const [categories, setCategories] = useState([]);
  const [prompts, setPrompts] = useState([]);
  const [filters, setFilters] = useState({
    model_name: '',
    category: '',
    prompt_id: '',
    success: ''
  });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch filter options
        const modelsData = await getModels();
        const categoriesData = await getCategories();
        const promptsData = await getPrompts({ limit: 100 });
        
        setModels(modelsData);
        setCategories(categoriesData);
        setPrompts(promptsData);
        
        // Fetch results with filters
        await fetchResults();
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    fetchResults();
  }, [filters, page]);

  const fetchResults = async () => {
    try {
      setLoading(true);
      
      // Prepare query parameters
      const params = {
        limit: itemsPerPage,
        skip: (page - 1) * itemsPerPage,
        ...filters
      };
      
      // Remove empty filters
      Object.keys(params).forEach(key => {
        if (params[key] === '') delete params[key];
      });
      
      // Convert success string to boolean if present
      if (params.success === 'true') params.success = true;
      if (params.success === 'false') params.success = false;
      
      const data = await getTestResults(params);
      setResults(data);
      
      // For simplicity, we're assuming there are more pages if we get a full page of results
      setTotalPages(Math.ceil(data.length / itemsPerPage) || 1);
    } catch (error) {
      console.error('Error fetching results:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters(prev => ({ ...prev, [name]: value }));
    setPage(1); // Reset to first page when filters change
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  // Find prompt text by ID
  const getPromptTextById = (promptId) => {
    const prompt = prompts.find(p => p.id === promptId);
    return prompt ? prompt.prompt_text : 'Prompt not found';
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Test Results
      </Typography>
      
      {/* Filters */}
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Filters
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel id="model-label">AI Model</InputLabel>
              <Select
                labelId="model-label"
                id="model_name"
                name="model_name"
                value={filters.model_name}
                label="AI Model"
                onChange={handleFilterChange}
              >
                <MenuItem value="">All Models</MenuItem>
                {models.map((model) => (
                  <MenuItem key={model} value={model}>
                    {model}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel id="category-label">Category</InputLabel>
              <Select
                labelId="category-label"
                id="category"
                name="category"
                value={filters.category}
                label="Category"
                onChange={handleFilterChange}
              >
                <MenuItem value="">All Categories</MenuItem>
                {categories.map((category) => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel id="prompt-label">Prompt</InputLabel>
              <Select
                labelId="prompt-label"
                id="prompt_id"
                name="prompt_id"
                value={filters.prompt_id}
                label="Prompt"
                onChange={handleFilterChange}
              >
                <MenuItem value="">All Prompts</MenuItem>
                {prompts.map((prompt) => (
                  <MenuItem key={prompt.id} value={prompt.id}>
                    {prompt.category} - {prompt.prompt_text.substring(0, 30)}...
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel id="success-label">Result</InputLabel>
              <Select
                labelId="success-label"
                id="success"
                name="success"
                value={filters.success}
                label="Result"
                onChange={handleFilterChange}
              >
                <MenuItem value="">All Results</MenuItem>
                <MenuItem value="true">Success</MenuItem>
                <MenuItem value="false">Failure</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button 
            variant="contained" 
            onClick={() => setFilters({
              model_name: '',
              category: '',
              prompt_id: '',
              success: ''
            })}
          >
            Clear Filters
          </Button>
        </Box>
      </Paper>
      
      {/* Results List */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {results.length > 0 ? (
            <Grid container spacing={3}>
              {results.map((result) => (
                <Grid item xs={12} key={result.id}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="h6" component="div">
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
                      
                      <Divider sx={{ mb: 2 }} />
                      
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <Typography variant="subtitle2" gutterBottom>
                            Prompt:
                          </Typography>
                          <Paper 
                            elevation={0} 
                            sx={{ 
                              p: 2, 
                              bgcolor: 'background.default',
                              maxHeight: '150px',
                              overflow: 'auto'
                            }}
                          >
                            <Typography variant="body2" className="prompt-text">
                              {getPromptTextById(result.prompt_id).substring(0, 200)}...
                            </Typography>
                          </Paper>
                          <Button 
                            size="small" 
                            component={RouterLink} 
                            to={`/prompts/${result.prompt_id}`}
                            sx={{ mt: 1 }}
                          >
                            View Full Prompt
                          </Button>
                        </Grid>
                        
                        <Grid item xs={12} md={6}>
                          <Typography variant="subtitle2" gutterBottom>
                            Response:
                          </Typography>
                          <Paper 
                            elevation={0} 
                            sx={{ 
                              p: 2, 
                              bgcolor: 'background.default',
                              maxHeight: '150px',
                              overflow: 'auto'
                            }}
                          >
                            <Typography variant="body2" className="response-text">
                              {result.response.substring(0, 200)}...
                            </Typography>
                          </Paper>
                        </Grid>
                      </Grid>
                      
                      <Box sx={{ mt: 2 }}>
                        {result.success_score !== undefined && (
                          <Typography variant="body2">
                            Success Score: {result.success_score}
                          </Typography>
                        )}
                        
                        {result.notes && (
                          <Typography variant="body2" sx={{ mt: 1 }}>
                            Notes: {result.notes}
                          </Typography>
                        )}
                      </Box>
                      
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
                        {result.category && (
                          <Chip 
                            label={`Category: ${result.category}`} 
                            size="small" 
                            color="primary"
                            variant="outlined"
                          />
                        )}
                        {result.challenge_id && (
                          <Chip 
                            label={`Challenge: ${result.challenge_id}`} 
                            size="small"
                            color="secondary"
                            variant="outlined"
                          />
                        )}
                        {result.run_id && (
                          <Chip 
                            label={`Run: ${result.run_id}`} 
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h6">
                No test results found
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                Try adjusting your filters or test some prompts.
              </Typography>
              <Button 
                variant="contained" 
                component={RouterLink} 
                to="/test"
                sx={{ mt: 2 }}
              >
                Go to Testing Interface
              </Button>
            </Paper>
          )}
          
          {/* Pagination */}
          {results.length > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination 
                count={totalPages} 
                page={page} 
                onChange={handlePageChange} 
                color="primary" 
              />
            </Box>
          )}
        </>
      )}
    </Box>
  );
};

export default ResultsList;