import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Divider,
  CircularProgress,
  Paper
} from '@mui/material';
import {
  FormatListBulleted as PromptIcon,
  Science as TestIcon,
  Assessment as ResultsIcon
} from '@mui/icons-material';
import { getPrompts, getTestResults, getModels, getChallenges } from '../../services/api';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    promptCount: 0,
    resultCount: 0,
    modelCount: 0,
    challengeCount: 0,
    recentPrompts: [],
    recentResults: []
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch prompts
        const prompts = await getPrompts({ limit: 5 });
        
        // Fetch results
        const results = await getTestResults({ limit: 5 });
        
        // Fetch models
        const models = await getModels();
        
        // Fetch challenges
        const challenges = await getChallenges();
        
        // Calculate challenge count
        let totalChallenges = 0;
        Object.values(challenges).forEach(waveArray => {
          totalChallenges += waveArray.length;
        });
        
        setStats({
          promptCount: prompts.length,
          resultCount: results.length,
          modelCount: models.length,
          challengeCount: totalChallenges,
          recentPrompts: prompts,
          recentResults: results
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
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
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      
      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card className="dashboard-card">
            <CardContent className="dashboard-card-content">
              <PromptIcon fontSize="large" color="primary" />
              <Typography variant="h5" component="div">
                {stats.promptCount}
              </Typography>
              <Typography color="text.secondary">
                Prompts
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" component={RouterLink} to="/prompts">
                View All
              </Button>
            </CardActions>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card className="dashboard-card">
            <CardContent className="dashboard-card-content">
              <ResultsIcon fontSize="large" color="primary" />
              <Typography variant="h5" component="div">
                {stats.resultCount}
              </Typography>
              <Typography color="text.secondary">
                Test Results
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" component={RouterLink} to="/results">
                View All
              </Button>
            </CardActions>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card className="dashboard-card">
            <CardContent className="dashboard-card-content">
              <TestIcon fontSize="large" color="primary" />
              <Typography variant="h5" component="div">
                {stats.modelCount}
              </Typography>
              <Typography color="text.secondary">
                AI Models
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" component={RouterLink} to="/test">
                Test Models
              </Button>
            </CardActions>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card className="dashboard-card">
            <CardContent className="dashboard-card-content">
              <PromptIcon fontSize="large" color="primary" />
              <Typography variant="h5" component="div">
                {stats.challengeCount}
              </Typography>
              <Typography color="text.secondary">
                Challenges
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" component={RouterLink} to="/prompts">
                View Prompts
              </Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>
      
      {/* Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Prompts
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {stats.recentPrompts.length > 0 ? (
              stats.recentPrompts.map((prompt) => (
                <Box key={prompt.id} sx={{ mb: 2 }}>
                  <Typography variant="subtitle1">
                    {prompt.category} - {prompt.technique || 'N/A'}
                  </Typography>
                  <Typography variant="body2" noWrap sx={{ mb: 1 }}>
                    {prompt.prompt_text.substring(0, 100)}...
                  </Typography>
                  <Button 
                    size="small" 
                    component={RouterLink} 
                    to={`/prompts/${prompt.id}`}
                    variant="outlined"
                  >
                    View Details
                  </Button>
                  <Divider sx={{ mt: 2 }} />
                </Box>
              ))
            ) : (
              <Typography variant="body2">No prompts found.</Typography>
            )}
            
            <Box sx={{ mt: 2 }}>
              <Button 
                variant="contained" 
                component={RouterLink} 
                to="/prompts"
              >
                View All Prompts
              </Button>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Test Results
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {stats.recentResults.length > 0 ? (
              stats.recentResults.map((result) => (
                <Box key={result.id} sx={{ mb: 2 }}>
                  <Typography variant="subtitle1">
                    {result.model_name} - {result.success ? 'Success' : 'Failure'}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Prompt ID: {result.prompt_id}
                  </Typography>
                  <Typography variant="body2" noWrap sx={{ mb: 1 }}>
                    {result.response.substring(0, 100)}...
                  </Typography>
                  <Divider sx={{ mt: 2 }} />
                </Box>
              ))
            ) : (
              <Typography variant="body2">No test results found.</Typography>
            )}
            
            <Box sx={{ mt: 2 }}>
              <Button 
                variant="contained" 
                component={RouterLink} 
                to="/results"
              >
                View All Results
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
      
      {/* Quick Actions */}
      <Paper elevation={2} sx={{ p: 2, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <Button 
              variant="contained" 
              fullWidth
              component={RouterLink} 
              to="/test"
              startIcon={<TestIcon />}
            >
              Test a Prompt
            </Button>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Button 
              variant="outlined" 
              fullWidth
              component={RouterLink} 
              to="/prompts"
              startIcon={<PromptIcon />}
            >
              Browse Prompts
            </Button>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Button 
              variant="outlined" 
              fullWidth
              component={RouterLink} 
              to="/results"
              startIcon={<ResultsIcon />}
            >
              View Results
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default Dashboard;