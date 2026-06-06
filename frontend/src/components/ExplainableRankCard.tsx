import React, { useState } from 'react';
import { 
  Card, 
  CardContent, 
  CardMedia, 
  Typography, 
  Box, 
  Button, 
  Collapse, 
  LinearProgress, 
  Rating, 
  Chip 
} from '@mui/material';
import { ChevronDown, ChevronUp, Tag, Sparkles } from 'lucide-react';

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

interface ExplainableRankCardProps {
  product: Product;
  relevanceScore: number;
  finalRankScore: number;
  featureContributions: Record<string, number>;
  onViewDetails: (productId: number) => void;
  onCartAdd?: (productId: number) => void;
}

export const ExplainableRankCard: React.FC<ExplainableRankCardProps> = ({
  product,
  relevanceScore,
  finalRankScore,
  featureContributions,
  onViewDetails,
  onCartAdd
}) => {
  const [expanded, setExpanded] = useState(false);
  
  // Format relevance score as match percentage
  const matchPct = Math.min(99, Math.round(relevanceScore * 100.0));
  
  const handleToggleExpand = (e: React.MouseEvent) => {
    e.stopPropagation();
    setExpanded(!expanded);
  };

  const getFeatureColor = (feature: string) => {
    if (feature.includes('Text')) return 'primary';
    if (feature.includes('Image')) return 'secondary';
    if (feature.includes('Rating')) return 'warning';
    return 'success';
  };

  return (
    <Card 
      className="hover-scale"
      sx={{ 
        backgroundColor: '#15171e', 
        border: '1px solid #2c2f3a', 
        borderRadius: 3, 
        overflow: 'hidden',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative'
      }}
    >
      {/* Match Score Badge */}
      <Box sx={{ position: 'absolute', top: 12, right: 12, zIndex: 1 }}>
        <Chip 
          icon={<Sparkles size={13} style={{ color: '#fff' }} />}
          label={`${matchPct}% Match`} 
          sx={{ 
            backgroundColor: 'rgba(63, 81, 181, 0.9)', 
            color: '#fff', 
            fontWeight: 700, 
            backdropFilter: 'blur(4px)',
            fontSize: '0.8rem'
          }} 
        />
      </Box>

      <CardMedia
        component="img"
        height="180"
        image={product.image_url || 'https://via.placeholder.com/260x180'}
        alt={product.title}
        sx={{ objectFit: 'cover', cursor: 'pointer', backgroundColor: '#0d0e12' }}
        onClick={() => onViewDetails(product.id)}
      />

      <CardContent sx={{ p: 2, display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
        {/* Brand */}
        <Typography variant="caption" sx={{ color: '#9aa0a6', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>
          {product.brand || 'Generic'}
        </Typography>

        {/* Title */}
        <Typography 
          variant="subtitle1" 
          onClick={() => onViewDetails(product.id)}
          sx={{ 
            color: '#f8f9fa', 
            fontWeight: 700, 
            lineHeight: 1.3, 
            my: 0.5,
            cursor: 'pointer',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            height: '40px',
            '&:hover': { color: '#757de8' }
          }}
        >
          {product.title}
        </Typography>

        {/* Rating */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Rating value={product.rating} precision={0.1} readOnly size="small" />
          <Typography variant="caption" sx={{ ml: 1, color: '#9aa0a6' }}>
            ({product.reviews_count})
          </Typography>
        </Box>

        {/* Price */}
        <Typography variant="h6" sx={{ color: '#ff4081', fontWeight: 800, mb: 1 }}>
          ₹{product.price.toLocaleString('en-IN')}
        </Typography>

        {/* Action Controls */}
        <Box sx={{ display: 'flex', gap: 1, mt: 'auto', borderTop: '1px solid #2c2f3a', pt: 1.5 }}>
          <Button 
            variant="text" 
            size="small" 
            onClick={handleToggleExpand}
            endIcon={expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            sx={{ color: '#9aa0a6', textTransform: 'none', fontWeight: 600, fontSize: '0.8rem' }}
          >
            Explain Rank
          </Button>
          
          <Button 
            variant="contained" 
            size="small" 
            onClick={() => onCartAdd?.(product.id)}
            sx={{ 
              ml: 'auto', 
              backgroundColor: '#3f51b5', 
              color: '#fff', 
              textTransform: 'none', 
              fontWeight: 700,
              '&:hover': { backgroundColor: '#757de8' }
            }}
          >
            Add to Cart
          </Button>
        </Box>

        {/* Expandable Explanation Drawer */}
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Box sx={{ mt: 2, p: 1.5, borderRadius: 2, backgroundColor: '#0d0e12', border: '1px solid #2c2f3a' }}>
            <Typography variant="caption" sx={{ color: '#757de8', fontWeight: 700, display: 'flex', alignItems: 'center', mb: 1, gap: 0.5 }}>
              <Sparkles size={12} /> FEATURE CONTRIBUTION WEIGHTS
            </Typography>
            
            {Object.entries(featureContributions).map(([feature, pct]) => (
              <Box key={feature} sx={{ mb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.2 }}>
                  <Typography variant="caption" sx={{ color: '#9aa0a6', fontSize: '0.7rem' }}>
                    {feature}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#f8f9fa', fontWeight: 700, fontSize: '0.7rem' }}>
                    {pct}%
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={pct} 
                  color={getFeatureColor(feature)} 
                  sx={{ height: 4, borderRadius: 2, backgroundColor: '#222' }} 
                />
              </Box>
            ))}
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};
