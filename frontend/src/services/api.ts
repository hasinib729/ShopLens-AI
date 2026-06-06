import axios from 'axios';

// API requests will be proxied by Vite dev server to http://localhost:8000
const api = axios.create({
  timeout: 15000,
});

export const searchAPI = {
  textSearch: async (query: string, sessionId: string, useRanker: boolean, experimentName?: string) => {
    const response = await api.post('/search/text', {
      query,
      session_id: sessionId,
      use_ranker: useRanker,
      experiment_name: experimentName
    });
    return response.data;
  },

  imageSearch: async (imageFile: File, sessionId: string) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('session_id', sessionId);
    const response = await api.post('/search/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  hybridSearch: async (query: string, imageFile: File, sessionId: string) => {
    const formData = new FormData();
    formData.append('query', query);
    formData.append('image', imageFile);
    formData.append('session_id', sessionId);
    const response = await api.post('/search/hybrid', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  autocomplete: async (query: string) => {
    const response = await api.get('/search/autocomplete', { params: { query } });
    return response.data;
  }
};

export const recAPI = {
  getRecommendations: async (sessionId: string, userId?: number, limit = 10) => {
    const response = await api.post('/recommendations', {
      session_id: sessionId,
      user_id: userId,
      limit
    });
    return response.data;
  },

  getSimilarProducts: async (productId: number) => {
    const response = await api.get(`/similar-products/${productId}`);
    return response.data;
  }
};

export const activityAPI = {
  logActivity: async (productId: number, sessionId: string, eventType: string, dwellTime = 0, userId?: number) => {
    const formData = new FormData();
    formData.append('product_id', String(productId));
    formData.append('session_id', sessionId);
    formData.append('event_type', eventType);
    formData.append('dwell_time', String(dwellTime));
    if (userId) formData.append('user_id', String(userId));
    
    const response = await api.post('/activity/log', formData);
    return response.data;
  }
};

export const abTestingAPI = {
  listExperiments: async () => {
    const response = await api.get('/api/experiments');
    return response.data;
  },
  
  logEvent: async (experimentName: string, sessionId: string, groupName: string, productId: number, action: string) => {
    const response = await api.post('/api/experiments/log', {
      experiment_name: experimentName,
      session_id: sessionId,
      group_name: groupName,
      product_id: productId,
      action
    });
    return response.data;
  }
};

export const analyticsAPI = {
  getOverview: async () => {
    const response = await api.get('/analytics/overview');
    return response.data;
  },

  getSearchAnalytics: async () => {
    const response = await api.get('/analytics/search');
    return response.data;
  },

  getRecommendationAnalytics: async () => {
    const response = await api.get('/analytics/recommendations');
    return response.data;
  },

  getEmbeddingsProjections: async () => {
    const response = await api.get('/analytics/embeddings');
    return response.data;
  },

  getModelMetrics: async () => {
    const response = await api.get('/model/metrics');
    return response.data;
  },

  getModelVersions: async () => {
    const response = await api.get('/model/versions');
    return response.data;
  },

  getModelDrift: async () => {
    const response = await api.get('/model/drift');
    return response.data;
  }
};
