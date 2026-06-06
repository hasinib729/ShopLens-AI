import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  Button, 
  Rating, 
  Chip, 
  Divider,
  Paper
} from '@mui/material';
import { ShoppingCart, Heart, ShieldCheck, Sparkles, ArrowLeft } from 'lucide-react';
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

interface ProductDetailsPageProps {
  sessionId: string;
  selectedProductId: number | null;
  onViewProduct: (productId: number) => void;
  onCartAdd: () => void;
  dbProducts: Product[]; // Catalog for local database lookup
}

export const ProductDetailsPage: React.FC<ProductDetailsPageProps> = ({
  sessionId,
  selectedProductId,
  onViewProduct,
  onCartAdd,
  dbProducts
}) => {
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [similarProducts, setSimilarProducts] = useState<any[]>([]);

  // Find product in local list and fetch similarities
  useEffect(() => {
    if (selectedProductId) {
      const p = dbProducts.find(item => item.id === selectedProductId);
      if (p) {
        setProduct(p);
        
        // Fetch similar products
        const fetchSimilar = async () => {
          try {
            const list = await recAPI.getSimilarProducts(p.id);
            setSimilarProducts(list);
          } catch (e) {
            console.error(e);
          }
        };
        fetchSimilar();
      }
    }
  }, [selectedProductId, dbProducts]);

  const handleCartAddWithLogging = async (pId: number) => {
    try {
      await activityAPI.logActivity(pId, sessionId, "cart");
      onCartAdd();
    } catch (e) {
      console.error(e);
    }
  };

  const handleProductView = async (pId: number) => {
    try {
      await activityAPI.logActivity(pId, sessionId, "view", 20);
      onViewProduct(pId);
      window.scrollTo(0, 0);
    } catch (e) {
      console.error(e);
    }
  };

  if (!product) {
    return (
      <Container sx={{ py: 8, textAlign: 'center' }}>
        <Typography variant="h6" sx={{ color: '#9aa0a6' }}>Product not found or select a product.</Typography>
        <Button startIcon={<ArrowLeft size={16} />} onClick={() => navigate('/')} sx={{ mt: 2, color: '#757de8' }}>
          Back to Search
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      
      {/* Back button */}
      <Button 
        startIcon={<ArrowLeft size={16} />} 
        onClick={() => navigate(-1)} 
        sx={{ color: '#9aa0a6', mb: 4, textTransform: 'none', fontWeight: 600 }}
      >
        Back
      </Button>

      <Grid container spacing={6} sx={{ mb: 8 }}>
        {/* Left column: image */}
        <Grid item xs={12} md={6}>
          <Paper 
            sx={{ 
              backgroundColor: '#15171e', 
              border: '1px solid #2c2f3a', 
              borderRadius: 4, 
              overflow: 'hidden', 
              display: 'flex', 
              justifyContent: 'center', 
              p: 2 
            }}
          >
            <Box 
              component="img" 
              src={product.image_url} 
              alt={product.title} 
              sx={{ width: '100%', maxHeight: 400, objectFit: 'contain', borderRadius: 3 }} 
            />
          </Paper>
        </Grid>

        {/* Right column: specifications */}
        <Grid item xs={12} md={6}>
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            
            {/* Brand */}
            <Typography variant="overline" sx={{ color: '#757de8', fontWeight: 800, letterSpacing: 1.5 }}>
              {product.brand || 'Generic'}
            </Typography>
            
            {/* Title */}
            <Typography variant="h4" sx={{ fontWeight: 800, mt: 1, mb: 2, color: '#fff' }}>
              {product.title}
            </Typography>

            {/* Ratings */}
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Rating value={product.rating} precision={0.1} readOnly />
              <Typography variant="body2" sx={{ ml: 1.5, color: '#9aa0a6', fontWeight: 600 }}>
                {product.rating} / 5.0 ({product.reviews_count} reviews)
              </Typography>
            </Box>

            <Divider sx={{ borderColor: '#2c2f3a', mb: 3 }} />

            {/* Price */}
            <Box sx={{ display: 'flex', alignItems: 'baseline', mb: 3 }}>
              <Typography variant="h3" sx={{ color: '#ff4081', fontWeight: 900 }}>
                ₹{product.price.toLocaleString('en-IN')}
              </Typography>
              <Typography variant="caption" sx={{ ml: 1.5, color: '#9aa0a6' }}>
                Inclusive of all taxes
              </Typography>
            </Box>

            {/* Description */}
            <Typography variant="body1" sx={{ color: '#9aa0a6', mb: 4, lineHeight: 1.6 }}>
              {product.description || 'No detailed description available for this item.'}
            </Typography>

            {/* Spec features list */}
            {product.features && (
              <Box sx={{ mb: 4 }}>
                <Typography variant="subtitle2" sx={{ color: '#fff', fontWeight: 700, mb: 1.5 }}>SPECIFICATIONS</Typography>
                <Grid container spacing={1}>
                  {Object.entries(product.features).map(([k, v]) => (
                    <Grid item xs={6} key={k}>
                      <Typography variant="caption" sx={{ color: '#9aa0a6', display: 'block', textTransform: 'uppercase' }}>{k}</Typography>
                      <Typography variant="body2" sx={{ color: '#fff', fontWeight: 600 }}>{String(v)}</Typography>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}

            {/* Actions */}
            <Box sx={{ display: 'flex', gap: 2, mt: 'auto' }}>
              <Button 
                variant="contained" 
                startIcon={<ShoppingCart size={18} />}
                onClick={() => handleCartAddWithLogging(product.id)}
                sx={{ 
                  flexGrow: 1, 
                  backgroundColor: '#3f51b5', 
                  color: '#fff', 
                  py: 1.5, 
                  borderRadius: 3, 
                  fontWeight: 700,
                  fontSize: '1rem',
                  textTransform: 'none',
                  '&:hover': { backgroundColor: '#757de8' }
                }}
              >
                Add to Cart
              </Button>
              
              <Button 
                variant="outlined" 
                sx={{ borderColor: '#2c2f3a', color: '#9aa0a6', px: 2, borderRadius: 3 }}
              >
                <Heart size={18} />
              </Button>
            </Box>

            {/* Shipping badge */}
            <Typography variant="caption" sx={{ color: '#34a853', display: 'flex', alignItems: 'center', gap: 0.5, mt: 2, fontWeight: 600 }}>
              <ShieldCheck size={14} /> Eligible for Free Express Delivery
            </Typography>

          </Box>
        </Grid>
      </Grid>

      {/* Similar Recommendations Slider */}
      <Box>
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Sparkles size={20} style={{ color: '#757de8' }} /> Customers Also Viewed (Retrieval-Augmented)
        </Typography>

        <Grid container spacing={3}>
          {similarProducts.map((card, idx) => (
            <Grid item xs={12} sm={6} md={2.4} key={card.product.id || idx}>
              <ExplainableRankCard
                product={card.product}
                relevanceScore={card.score}
                finalRankScore={card.score}
                featureContributions={{"Text Similarity": 35, "Image Similarity": 35, "Rating Score": 15, "Popularity": 15}}
                onViewDetails={handleProductView}
                onCartAdd={handleCartAddWithLogging}
              />
            </Grid>
          ))}
        </Grid>
      </Box>

    </Container>
  );
};
