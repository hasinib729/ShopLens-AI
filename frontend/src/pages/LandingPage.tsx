import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  TextField, 
  Button, 
  Card, 
  CardContent, 
  Grid, 
  IconButton, 
  Chip 
} from '@mui/material';
import { Search, Camera, Sparkles, TrendingUp, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { searchAPI, recAPI, activityAPI } from '../services/api';
import { ExplainableRankCard } from '../components/ExplainableRankCard';

interface LandingPageProps {
  sessionId: string;
  onTextSearch: (query: string) => void;
  onImageSearch: (file: File) => void;
  onHybridSearch: (query: string, file: File) => void;
  onViewProduct: (productId: number) => void;
  onCartAdd: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  sessionId,
  onTextSearch,
  onImageSearch,
  onHybridSearch,
  onViewProduct,
  onCartAdd
}) => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [trendingProducts, setTrendingProducts] = useState<any[]>([]);

  // Fetch trending products (uses recommendations internally)
  useEffect(() => {
    const fetchTrending = async () => {
      try {
        const res = await recAPI.getRecommendations(sessionId, undefined, 4);
        setTrendingProducts(res.recommendations);
      } catch (e) {
        console.error(e);
      }
    };
    fetchTrending();
  }, [sessionId]);

  const handleSearchSubmit = () => {
    if (selectedFile && query) {
      // Hybrid search
      onHybridSearch(query, selectedFile);
      navigate('/results');
    } else if (selectedFile) {
      // Visual search
      onImageSearch(selectedFile);
      navigate('/results');
    } else if (query.trim()) {
      // Text search
      onTextSearch(query);
      navigate('/results');
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleClearImage = () => {
    setSelectedFile(null);
    setImagePreview(null);
  };

  const handleCategoryClick = (categoryName: string) => {
    onTextSearch(categoryName);
    navigate('/results');
  };

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
      await activityAPI.logActivity(pId, sessionId, "view", 15);
      onViewProduct(pId);
      navigate('/details');
    } catch (e) {
      console.error(e);
    }
  };

  const categories = [
    { name: "Running Shoes", count: "820 Products" },
    { name: "Handbags", count: "450 Products" },
    { name: "Smartwatches", count: "310 Products" },
    { name: "Gaming Mouse", count: "290 Products" },
    { name: "Formal Shirts", count: "540 Products" }
  ];

  return (
    <Box sx={{ py: 6 }}>
      
      {/* Animated Hero Header */}
      <Container maxWidth="md" sx={{ textAlign: 'center', mb: 8 }}>
        <Chip 
          icon={<Sparkles size={13} style={{ color: '#757de8' }} />} 
          label="Next-Gen Intelligent Retrieval" 
          variant="outlined" 
          sx={{ color: '#757de8', border: '1px solid #757de8', mb: 3, fontWeight: 700 }}
        />
        
        <Typography 
          variant="h2" 
          sx={{ 
            fontFamily: 'Outfit', 
            fontWeight: 900, 
            lineHeight: 1.15,
            letterSpacing: '-0.03em',
            mb: 2,
            background: 'linear-gradient(to right, #fff, #9aa0a6)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          Discover Products beyond keywords
        </Typography>

        <Typography variant="h6" sx={{ color: '#9aa0a6', fontWeight: 500, mb: 5, maxWidth: 600, mx: 'auto' }}>
          Search catalog items using text, images, or combining visual similarity and textual intent.
        </Typography>

        {/* Multi-modal search input board */}
        <Card sx={{ backgroundColor: '#15171e', border: '1px solid #2c2f3a', borderRadius: 4, p: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            
            {/* Camera Upload Trigger */}
            <input 
              accept="image/*" 
              style={{ display: 'none' }} 
              id="hero-camera-upload" 
              type="file" 
              onChange={handleFileChange}
            />
            <label htmlFor="hero-camera-upload">
              <IconButton component="span" sx={{ color: '#757de8', backgroundColor: '#0d0e12', p: 1.5, border: '1px solid #2c2f3a' }}>
                <Camera size={20} />
              </IconButton>
            </label>

            {/* Input Bar */}
            <TextField
              fullWidth
              variant="outlined"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={selectedFile ? "Add filters (e.g. 'under 3000', 'color black')" : "Ask for 'red sneakers under 4000'..."}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSearchSubmit();
              }}
              InputProps={{
                style: { color: '#fff', backgroundColor: '#0d0e12', borderRadius: 12 },
                endAdornment: (
                  <Button 
                    variant="contained" 
                    onClick={handleSearchSubmit}
                    startIcon={<Search size={16} />}
                    sx={{ 
                      backgroundColor: '#3f51b5', 
                      color: '#fff', 
                      borderRadius: 2,
                      px: 3,
                      '&:hover': { backgroundColor: '#757de8' }
                    }}
                  >
                    Search
                  </Button>
                )
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '& fieldset': { borderColor: '#2c2f3a' },
                  '&:hover fieldset': { borderColor: '#3f51b5' },
                }
              }}
            />
          </Box>

          {/* Image Upload Preview */}
          {imagePreview && (
            <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 2, p: 1, backgroundColor: '#0d0e12', borderRadius: 2, border: '1px solid #2c2f3a' }}>
              <Box 
                component="img" 
                src={imagePreview} 
                alt="Upload preview" 
                sx={{ width: 60, height: 60, borderRadius: 1.5, objectFit: 'cover' }} 
              />
              <Box sx={{ textAlign: 'left', flexGrow: 1 }}>
                <Typography variant="caption" sx={{ color: '#9aa0a6', display: 'block' }}>Visual Search File Active</Typography>
                <Typography variant="subtitle2" sx={{ color: '#fff' }}>{selectedFile?.name}</Typography>
              </Box>
              <Button size="small" variant="text" color="error" onClick={handleClearImage}>
                Remove
              </Button>
            </Box>
          )}
        </Card>
      </Container>

      {/* Popular Categories */}
      <Container maxWidth="lg" sx={{ mb: 8 }}>
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
          <TrendingUp size={20} style={{ color: '#ff4081' }} /> Popular Categories
        </Typography>
        <Grid container spacing={2}>
          {categories.map((c) => (
            <Grid item xs={6} sm={4} md={2.4} key={c.name}>
              <Card 
                onClick={() => handleCategoryClick(c.name)}
                sx={{ 
                  backgroundColor: '#15171e', 
                  border: '1px solid #2c2f3a', 
                  borderRadius: 3,
                  cursor: 'pointer',
                  textAlign: 'center',
                  py: 3,
                  transition: 'all 0.2s',
                  '&:hover': { borderColor: '#3f51b5', transform: 'translateY(-2px)' }
                }}
              >
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#fff' }}>
                  {c.name}
                </Typography>
                <Typography variant="caption" sx={{ color: '#9aa0a6' }}>
                  {c.count}
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Trending Products */}
      <Container maxWidth="lg">
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Sparkles size={20} style={{ color: '#757de8' }} /> Trending Recommendations
        </Typography>
        
        <Grid container spacing={3}>
          {trendingProducts.map((card, idx) => (
            <Grid item xs={12} sm={6} md={3} key={card.product.id || idx}>
              <ExplainableRankCard
                product={card.product}
                relevanceScore={card.score}
                finalRankScore={card.score}
                featureContributions={{"Text Similarity": 40, "Image Similarity": 30, "Rating Score": 15, "Popularity": 15}}
                onViewDetails={handleProductView}
                onCartAdd={handleCartAddWithLogging}
              />
            </Grid>
          ))}
        </Grid>
      </Container>

    </Box>
  );
};
