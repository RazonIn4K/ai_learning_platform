import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
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
  Typography,
  Pagination
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Science as TestIcon
} from '@mui/icons-material';
import { getPrompts, getCategories, getChallenges, getTechniques, deletePrompt } from '../../services/api';

const PromptList = () => {
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [techniques, setTechniques] = useState([]);
  const [challenges, setChallenges] = useState({});
  const [filters, setFilters] = useState({
    category: '',
    technique: '',
    challenge_id: '',
    search: ''
  });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 10;

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
        
        // Fetch prompts with filters
        await fetchPrompts();
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    fetchPrompts();
  }, [filters, page]);

  const fetchPrompts = async () => {
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
        if (!params[key]) delete params[key];
      });
      
      const data = await getPrompts(params);
      setPrompts(data);
      
      // For simplicity, we're assuming there are more pages if we get a full page of results
      setTotalPages(Math.ceil(data.length / itemsPerPage) || 1);
    } catch (error) {
      console.error('Error fetching prompts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters(prev => ({ ...prev, [name]: value }));
    setPage(1); // Reset to first page when filters change
  };

  const handleSearchChange = (event) => {
    const { value } = event.target;
    setFilters(prev => ({ ...prev, search: value }));
    setPage(1); // Reset to first page when search changes
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const handleCopyPrompt = (promptText) => {
    navigator.clipboard.writeText(promptText)
      .then(() => {
        alert('Prompt copied to clipboard!');
      })
      .catch(err => {
        console.error('Failed to copy prompt:', err);
        alert('Failed to copy prompt. Please try again.');
      });
  };

  const handleDeletePrompt = async (id) => {
    if (window.confirm('Are you sure you want to delete this prompt?')) {
      try {
        await deletePrompt(id);
        // Refresh prompts after deletion
        fetchPrompts();
      } catch (error) {
        console.error('Error deleting prompt:', error);
        alert('Failed to delete prompt. Please try again.');
      }
    }
  };

  // Flatten challenges for the filter dropdown
  const flattenedChallenges = Object.entries(challenges).reduce((acc, [wave, waveItems]) => {
    waveItems.forEach(item => {
      acc.push({ id: item, name: `${wave}: ${item}` });
    });
    return acc;
  }, []);

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Prompts
      </Typography>
      
      {/* Filters */}
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Filters
        </Typography>
        <Grid container spacing={2}>
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
              <InputLabel id="technique-label">Technique</InputLabel>
              <Select
                labelId="technique-label"
                id="technique"
                name="technique"
                value={filters.technique}
                label="Technique"
                onChange={handleFilterChange}
              >
                <MenuItem value="">All Techniques</MenuItem>
                {techniques.map((technique) => (
                  <MenuItem key={technique} value={technique}>
                    {technique}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel id="challenge-label">Challenge</InputLabel>
              <Select
                labelId="challenge-label"
                id="challenge_id"
                name="challenge_id"
                value={filters.challenge_id}
                label="Challenge"
                onChange={handleFilterChange}
              >
                <MenuItem value="">All Challenges</MenuItem>
                {flattenedChallenges.map((challenge) => (
                  <MenuItem key={challenge.id} value={challenge.id}>
                    {challenge.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              id="search"
              name="search"
              label="Search"
              value={filters.search}
              onChange={handleSearchChange}
            />
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button 
            variant="contained" 
            onClick={() => setFilters({
              category: '',
              technique: '',
              challenge_id: '',
              search: ''
            })}
          >
            Clear Filters
          </Button>
        </Box>
      </Paper>
      
      {/* Prompts List */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {prompts.length > 0 ? (
            <Grid container spacing={3}>
              {prompts.map((prompt) => (
                <Grid item xs={12} key={prompt.id}>
                  <Card className="prompt-card">
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="h6" component="div">
                          {prompt.category}
                          {prompt.technique && (
                            <Chip 
                              label={prompt.technique} 
                              size="small" 
                              sx={{ ml: 1 }}
                            />
                          )}
                        </Typography>
                        <Box>
                          <IconButton 
                            size="small" 
                            onClick={() => handleCopyPrompt(prompt.prompt_text)}
                            title="Copy prompt"
                          >
                            <CopyIcon />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            component={RouterLink} 
                            to={`/test?promptId=${prompt.id}`}
                            title="Test prompt"
                          >
                            <TestIcon />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            component={RouterLink} 
                            to={`/prompts/${prompt.id}`}
                            title="Edit prompt"
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            onClick={() => handleDeletePrompt(prompt.id)}
                            title="Delete prompt"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      </Box>
                      
                      <Divider sx={{ mb: 2 }} />
                      
                      <Typography 
                        variant="body2" 
                        className="prompt-text"
                        sx={{ mb: 2, maxHeight: '100px', overflow: 'auto' }}
                      >
                        {prompt.prompt_text.length > 300 
                          ? `${prompt.prompt_text.substring(0, 300)}...` 
                          : prompt.prompt_text
                        }
                      </Typography>
                      
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {prompt.challenge_id && (
                          <Chip 
                            label={`Challenge: ${prompt.challenge_id}`} 
                            size="small" 
                            color="primary"
                            variant="outlined"
                          />
                        )}
                        {prompt.status && (
                          <Chip 
                            label={`Status: ${prompt.status}`} 
                            size="small"
                            color={prompt.status === 'tested' ? 'success' : 'default'}
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </CardContent>
                    <CardActions>
                      <Button 
                        size="small" 
                        component={RouterLink} 
                        to={`/prompts/${prompt.id}`}
                      >
                        View Details
                      </Button>
                      <Button 
                        size="small" 
                        component={RouterLink} 
                        to={`/test?promptId=${prompt.id}`}
                      >
                        Test Prompt
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h6">
                No prompts found
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                Try adjusting your filters or create a new prompt.
              </Typography>
            </Paper>
          )}
          
          {/* Pagination */}
          {prompts.length > 0 && (
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
      
      {/* Create New Prompt Button */}
      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <Button 
          variant="contained" 
          component={RouterLink} 
          to="/prompts/new"
          size="large"
        >
          Create New Prompt
        </Button>
      </Box>
    </Box>
  );
};

export default PromptList;