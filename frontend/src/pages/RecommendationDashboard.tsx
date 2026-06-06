import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Grid, 
  Alert, 
  Snackbar, 
  Button,
  Chip
} from '@mui/material';
import { Compass, Sparkles, RefreshCw, Zap } from 'lucide-react';
import { recAPI, activityAPI } from '../services/api';
import { ExplainableRankCard } from '../components/ExplainableRankCard';
import { useNavigate } from 'react-router-dom';

interface Product {
  id: number;
  product_id: string;
  title: string;
  description?: string;
  brand?: string;
  category?: string;
  price: number;
  image_url?: string;
  rating: number;
  reviews_count: number;
  features?: any;
}

interface RecommendationDashboardProps {
  sessionId: string;
  onViewProduct: (productId: number) => void;
  onCartAdd: () => void;
  liveRefreshAlert: boolean;
  onClearLiveAlert: () => void;
}

export const RecommendationDashboard: React.FC<RecommendationDashboardProps> = ({
  sessionId,
  onViewProduct,
  onCartAdd,
  liveRefreshAlert,
  onClearLiveAlert
}) => {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [historyProducts, setHistoryProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchFeeds = async () => {
    setLoading(true);
    try {
      // Fetch personalized items
      const res = await recAPI.getRecommendations(sessionId, undefined, 8);
      setRecommendations(res.recommendations);
      
      // Fetch user click logs/view history
      // In local mode, simulate recent history by taking some products from seed catalog
      // In main main app, we can just load the products
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeeds();
  }, [sessionId]);

  const handleRefreshClick = () => {
    fetchFeeds();
    onClearLiveAlert();
  };

  const handleCartAddWithLogging = async (pId: number) => {
    try {
      await activityAPI.logActivity(pId, sessionId, "cart");
      onCartAdd();
      // Refetches list immediately
      fetchFeeds();
    } catch (e) {
      console.error(e);
    }
  };

  const handleProductView = async (pId: number) => {
    try {
      await activityAPI.logActivity(pId, sessionId, "view", 15);
      onViewProduct(pId);
      navigate('/details');
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 6 }}>
      
      {/* Live websocket notifications snackbar */}
      <Snackbar 
        open={liveRefreshAlert} 
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        onClose={onClearLiveAlert}
      >
        <Alert 
          severity="info" 
          icon={<Zap size={16} />}
          action={
            <Button color="inherit" size="small" startIcon={<RefreshCw size={14} />} onClick={handleRefreshClick}>
              Refresh
            </Button>
          }
          sx={{ border: '1px solid #29b6f6', color: '#fff', backgroundColor: '#15171e' }}
        >
          Real-time activity detected. Updates are ready!
        </Alert>
      </Snackbar>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 5 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Compass size={32} style={{ color: '#757de8' }} /> Your Personal Discovery Feed
          </Typography>
          <Typography variant="body2" sx={{ color: '#9aa0a6', mt: 0.5 }}>
            Personalized using Two-Tower Collaborative Filtering, updated in real-time as you browse.
          </Typography>
        </Box>
        
        <Button 
          variant="outlined" 
          startIcon={<RefreshCw size={16} />} 
          onClick={fetchFeeds}
          disabled={loading}
          sx={{ 
            borderColor: '#2c2f3a', 
            color: '#9aa0a6', 
            borderRadius: 3, 
            textTransform: 'none', 
            fontWeight: 600,
            '&:hover': { color: '#fff', borderColor: '#757de8' }
          }}
        >
          {loading ? 'Refreshing...' : 'Refresh Feed'}
        </Button>
      </Box>

      {/* Main personalized results */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Sparkles size={20} style={{ color: '#ff4081' }} /> Recommended For You
        </Typography>

        {loading ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <RefreshCw size={36} className="animate-spin" style={{ color: '#757de8' }} />
          </Box>
        ) : recommendations.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 6, backgroundColor: '#15171e', borderRadius: 4, border: '1px solid #2c2f3a' }}>
            <Typography variant="subtitle1" sx={{ color: '#9aa0a6' }}>Your feed is empty.</Typography>
            <Typography variant="caption" sx={{ color: '#9aa0a6', display: 'block', mt: 1 }}>
              Browse the catalog and view products to build your profile vectors.
            </Typography>
          </Box>
        ) : (
          <Grid container spacing={3}>
            {recommendations.map((card, idx) => (
              <Grid item xs={12} sm={6} md={3} key={card.product.id || idx}>
                <ExplainableRankCard
                  product={card.product}
                  relevanceScore={card.score}
                  finalRankScore={card.score}
                  featureContributions={{"Text Similarity": 45, "Image Similarity": 25, "Rating Score": 15, "Popularity": 15}}
                  onViewDetails={handleProductView}
                  onCartAdd={handleCartAddWithLogging}
                />
              </Grid>
            ))}
          </Grid>
        )}
      </Box>

    </Container>
  );
};
