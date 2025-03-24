import axios from 'axios';

// Base API URL - using proxy in development
const API_URL = '';

// Prompts API
export const getPrompts = async (params = {}) => {
  try {
    const response = await axios.get(`${API_URL}/api/prompts`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching prompts:', error);
    throw error;
  }
};

export const getPromptById = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/api/prompts/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching prompt ${id}:`, error);
    throw error;
  }
};

export const createPrompt = async (promptData) => {
  try {
    const response = await axios.post(`${API_URL}/api/prompts`, promptData);
    return response.data;
  } catch (error) {
    console.error('Error creating prompt:', error);
    throw error;
  }
};

export const updatePrompt = async (id, promptData) => {
  try {
    const response = await axios.put(`${API_URL}/api/prompts/${id}`, promptData);
    return response.data;
  } catch (error) {
    console.error(`Error updating prompt ${id}:`, error);
    throw error;
  }
};

export const deletePrompt = async (id) => {
  try {
    const response = await axios.delete(`${API_URL}/api/prompts/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting prompt ${id}:`, error);
    throw error;
  }
};

// Test Results API
export const getTestResults = async (params = {}) => {
  try {
    const response = await axios.get(`${API_URL}/api/results`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching test results:', error);
    throw error;
  }
};

export const createTestResult = async (resultData) => {
  try {
    const response = await axios.post(`${API_URL}/api/results`, resultData);
    return response.data;
  } catch (error) {
    console.error('Error creating test result:', error);
    throw error;
  }
};

// Utility APIs
export const getModels = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/models`);
    return response.data.models;
  } catch (error) {
    console.error('Error fetching models:', error);
    throw error;
  }
};

export const getChallenges = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/challenges`);
    return response.data.challenges;
  } catch (error) {
    console.error('Error fetching challenges:', error);
    throw error;
  }
};

export const getCategories = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/categories`);
    return response.data.categories;
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw error;
  }
};

export const getTechniques = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/techniques`);
    return response.data.techniques;
  } catch (error) {
    console.error('Error fetching techniques:', error);
    throw error;
  }
};