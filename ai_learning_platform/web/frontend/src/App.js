import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import { useAuth } from './contexts/AuthContext';

// Components
import Header from './components/layout/Header';
import Login from './components/auth/Login';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Dashboard from './components/dashboard/Dashboard';
import PromptList from './components/prompts/PromptList';
import PromptDetail from './components/prompts/PromptDetail';
import TestInterface from './components/testing/TestInterface';
import ResultsList from './components/results/ResultsList';
import ManualTestingInterface from './components/testing/ManualTestingInterface';
import EnhancedTestingInterface from './components/testing/EnhancedTestingInterface';

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <Container component="main" sx={{ flexGrow: 1, py: 4 }}>
        <Routes>
          <Route path="/login" element={
            isAuthenticated ? <Navigate to="/" /> : <Login />
          } />
          
          <Route path="/" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          
          <Route path="/prompts" element={
            <ProtectedRoute>
              <PromptList />
            </ProtectedRoute>
          } />
          
          <Route path="/prompts/:id" element={
            <ProtectedRoute>
              <PromptDetail />
            </ProtectedRoute>
          } />
          
          <Route path="/test" element={
            <ProtectedRoute>
              <TestInterface />
            </ProtectedRoute>
          } />

          <Route path="/manual-test" element={
            <ProtectedRoute>
              <ManualTestingInterface />
            </ProtectedRoute>
          } />
          
          <Route path="/enhanced-test" element={
            <ProtectedRoute>
              <EnhancedTestingInterface />
            </ProtectedRoute>
          } />
          
          <Route path="/results" element={
            <ProtectedRoute>
              <ResultsList />
            </ProtectedRoute>
          } />
          
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Container>
    </Box>
  );
}

export default App;