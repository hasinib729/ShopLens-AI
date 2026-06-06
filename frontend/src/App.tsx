import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { Navbar } from './components/Navbar';
import { LandingPage } from './pages/LandingPage';
import { SearchResultsPage } from './pages/SearchResultsPage';
import { ProductDetailsPage } from './pages/ProductDetailsPage';
import { RecommendationDashboard } from './pages/RecommendationDashboard';
import { AdminDashboard } from './pages/AdminDashboard';
import { searchAPI, analyticsAPI } from './services/api';

// Dark premium MUI theme matching our index.css design tokens
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#757de8' },
    secondary: { main: '#ff4081' },
    background: { default: '#0d0e12', paper: '#15171e' },
    text: { primary: '#f8f9fa', secondary: '#9aa0a6' }
  },
  typography: {
    fontFamily: '"Inter", "Helvetica", "Arial", sans-serif',
    h1: { fontFamily: '"Outfit", sans-serif' },
    h2: { fontFamily: '"Outfit", sans-serif' },
    h3: { fontFamily: '"Outfit", sans-serif' },
    h4: { fontFamily: '"Outfit", sans-serif' },
    h5: { fontFamily: '"Outfit", sans-serif' },
    h6: { fontFamily: '"Outfit", sans-serif' }
  }
});

// Helper to generate a session_id
const generateSessionId = () => {
  return 'sess_' + Math.random().toString(36).substring(2, 14);
};

export const App: React.FC = () => {
  const [sessionId] = useState(() => generateSessionId());
  const [cartCount, setCartCount] = useState(0);
  const [searchResults, setSearchResults] = useState<any>(null);
  const [searchType, setSearchType] = useState('text');
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [liveRefreshAlert, setLiveRefreshAlert] = useState(false);
  const [dbProducts, setDbProducts] = useState<any[]>([]);

  // 1. Fetch catalog products on startup
  useEffect(() => {
    const fetchCatalog = async () => {
      try {
        const list = await analyticsAPI.getEmbeddingsProjections();
        // Map projections back to Product structure
        const productsList = list.map((item: any) => ({
          id: item.id,
          product_id: `PROD${item.id}`,
          title: item.title,
          description: `Premium catalog ${item.category} designed by ${item.brand}.`,
          brand: item.brand,
          category: item.category,
          price: item.price,
          image_url: item.image_url,
          rating: 4.5,
          reviews_count: 85
        }));
        setDbProducts(productsList);
      } catch (e) {
        console.error("Failed to load catalog products: ", e);
      }
    };
    fetchCatalog();
  }, []);

  // 2. Connect WebSockets for live updates
  useEffect(() => {
    const wsUrl = `ws://${window.location.hostname}:8000/ws/${sessionId}`;
    let socket: WebSocket;
    
    const connect = () => {
      socket = new WebSocket(wsUrl);
      
      socket.onopen = () => {
        console.log("Connected to live WebSockets channel.");
      };
      
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event === "recommendation_refresh") {
            setLiveRefreshAlert(true);
          }
        } catch (e) {
          console.error(e);
        }
      };
      
      socket.onclose = () => {
        // Retry connection in 3 seconds
        setTimeout(connect, 3000);
      };
    };
    
    connect();
    return () => {
      if (socket) socket.close();
    };
  }, [sessionId]);

  // 3. Search triggers handlers
  const handleTextSearch = async (query: string) => {
    setLoading(true);
    setSearchType('text');
    try {
      const res = await searchAPI.textSearch(query, sessionId, true);
      setSearchResults(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleImageSearch = async (file: File) => {
    setLoading(true);
    setSearchType('image');
    try {
      const res = await searchAPI.imageSearch(file, sessionId);
      setSearchResults(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleHybridSearch = async (query: string, file: File) => {
    setLoading(true);
    setSearchType('hybrid');
    try {
      const res = await searchAPI.hybridSearch(query, file, sessionId);
      setSearchResults(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleViewProduct = (productId: number) => {
    setSelectedProductId(productId);
  };

  const handleCartAdd = () => {
    setCartCount(prev => prev + 1);
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#0d0e12' }}>
          
          <Navbar 
            sessionId={sessionId} 
            cartCount={cartCount} 
            onTextSearch={handleTextSearch} 
          />

          <Box sx={{ flexGrow: 1 }}>
            <Routes>
              <Route 
                path="/" 
                element={
                  <LandingPage 
                    sessionId={sessionId}
                    onTextSearch={handleTextSearch}
                    onImageSearch={handleImageSearch}
                    onHybridSearch={handleHybridSearch}
                    onViewProduct={handleViewProduct}
                    onCartAdd={handleCartAdd}
                  />
                } 
              />
              <Route 
                path="/results" 
                element={
                  <SearchResultsPage 
                    sessionId={sessionId}
                    searchResults={searchResults}
                    searchType={searchType}
                    loading={loading}
                    onViewProduct={handleViewProduct}
                    onCartAdd={handleCartAdd}
                  />
                } 
              />
              <Route 
                path="/details" 
                element={
                  <ProductDetailsPage 
                    sessionId={sessionId}
                    selectedProductId={selectedProductId}
                    onViewProduct={handleViewProduct}
                    onCartAdd={handleCartAdd}
                    dbProducts={dbProducts}
                  />
                } 
              />
              <Route 
                path="/recommendations" 
                element={
                  <RecommendationDashboard 
                    sessionId={sessionId}
                    onViewProduct={handleViewProduct}
                    onCartAdd={handleCartAdd}
                    liveRefreshAlert={liveRefreshAlert}
                    onClearLiveAlert={() => setLiveRefreshAlert(false)}
                  />
                } 
              />
              <Route 
                path="/admin" 
                element={<AdminDashboard />} 
              />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App;
