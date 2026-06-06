import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  Slider, 
  FormGroup, 
  FormControlLabel, 
  Checkbox, 
  RadioGroup, 
  Radio, 
  Select, 
  MenuItem, 
  InputLabel, 
  FormControl, 
  CircularProgress,
  Divider,
  Paper
} from '@mui/material';
import { Sparkles, SlidersHorizontal, ArrowUpDown } from 'lucide-react';
import { ExplainableRankCard } from '../components/ExplainableRankCard';
import { activityAPI } from '../services/api';

interface SearchResultsPageProps {
  sessionId: string;
  searchResults: any;
  searchType: string;
  loading: boolean;
  onViewProduct: (productId: number) => void;
  onCartAdd: () => void;
}

export const SearchResultsPage: React.FC<SearchResultsPageProps> = ({
  sessionId,
  searchResults,
  searchType,
  loading,
  onViewProduct,
  onCartAdd
}) => {
  const [results, setResults] = useState<any[]>([]);
  const [filteredResults, setFilteredResults] = useState<any[]>([]);
  const [priceRange, setPriceRange] = useState<number[]>([0, 50000]);
  const [selectedBrands, setSelectedBrands] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [minRating, setMinRating] = useState<number>(0);
  const [sortBy, setSortBy] = useState<string>('rank');

  useEffect(() => {
    if (searchResults && searchResults.results) {
      setResults(searchResults.results);
      setFilteredResults(searchResults.results);
      
      // Auto set price bounds from search results
      const prices = searchResults.results.map((r: any) => r.product.price);
      if (prices.length > 0) {
        const max = Math.max(...prices);
        setPriceRange([0, Math.ceil(max)]);
      }
    }
  }, [searchResults]);

  // Apply UI post-retrieval filters
  useEffect(() => {
    let list = [...results];
    
    // Price filter
    list = list.filter(r => r.product.price >= priceRange[0] && r.product.price <= priceRange[1]);
    
    // Category filter
    if (selectedCategory !== 'all') {
      list = list.filter(r => r.product.category === selectedCategory);
    }
    
    // Brand filter
    if (selectedBrands.length > 0) {
      list = list.filter(r => selectedBrands.includes(r.product.brand));
    }
    
    // Rating filter
    if (minRating > 0) {
      list = list.filter(r => r.product.rating >= minRating);
    }
    
    // Sorting
    if (sortBy === 'price-low') {
      list.sort((a, b) => a.product.price - b.product.price);
    } else if (sortBy === 'price-high') {
      list.sort((a, b) => b.product.price - a.product.price);
    } else if (sortBy === 'rating') {
      list.sort((a, b) => b.product.rating - a.product.rating);
    } else {
      // Sort by final rank score (LTR)
      list.sort((a, b) => b.final_rank_score - a.final_rank_score);
    }
    
    setFilteredResults(list);
  }, [priceRange, selectedBrands, selectedCategory, minRating, sortBy, results]);

  const handleBrandChange = (brandName: string) => {
    if (selectedBrands.includes(brandName)) {
      setSelectedBrands(selectedBrands.filter(b => b !== brandName));
    } else {
      setSelectedBrands([...selectedBrands, brandName]);
    }
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
      await activityAPI.logActivity(pId, sessionId, "view", 25);
      onViewProduct(pId);
    } catch (e) {
      console.error(e);
    }
  };

  // Extract distinct brands from current search subset
  const distinctBrands = Array.from(new Set(results.map(r => r.product.brand).filter(Boolean))) as string[];
  const distinctCategories = Array.from(new Set(results.map(r => r.product.category).filter(Boolean))) as string[];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: 2 }}>
        <CircularProgress size={50} sx={{ color: '#757de8' }} />
        <Typography variant="h6" sx={{ color: '#9aa0a6' }}>Processing multi-modal vectors...</Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800 }}>Search Results</Typography>
          {searchResults && (
            <Typography variant="body2" sx={{ color: '#9aa0a6', mt: 0.5 }}>
              Found {filteredResults.length} items in {searchResults.latency_ms?.toFixed(1)}ms using {searchType.toUpperCase()} search mode
            </Typography>
          )}
        </Box>

        {/* Sort drop dropdown */}
        <FormControl size="small" sx={{ width: 180, '& .MuiOutlinedInput-root': { borderColor: '#2c2f3a', color: '#fff' } }}>
          <InputLabel sx={{ color: '#9aa0a6' }}>Sort By</InputLabel>
          <Select
            value={sortBy}
            label="Sort By"
            onChange={(e) => setSortBy(e.target.value)}
            sx={{ backgroundColor: '#15171e', borderRadius: 2 }}
          >
            <MenuItem value="rank">Recommended (LTR)</MenuItem>
            <MenuItem value="price-low">Price: Low to High</MenuItem>
            <MenuItem value="price-high">Price: High to Low</MenuItem>
            <MenuItem value="rating">Top Rated</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={4}>
        {/* Sidebar Filters */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3, backgroundColor: '#15171e', border: '1px solid #2c2f3a', borderRadius: 4 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
              <SlidersHorizontal size={18} style={{ color: '#757de8' }} /> Filters
            </Typography>
            
            <Divider sx={{ my: 2, borderColor: '#2c2f3a' }} />

            {/* Price Filter */}
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, color: '#fff' }}>Price Range</Typography>
            <Slider
              value={priceRange}
              onChange={(_, value) => setPriceRange(value as number[])}
              valueLabelDisplay="auto"
              min={0}
              max={50000}
              sx={{ color: '#3f51b5' }}
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
              <Typography variant="caption" sx={{ color: '#9aa0a6' }}>₹{priceRange[0]}</Typography>
              <Typography variant="caption" sx={{ color: '#9aa0a6' }}>₹{priceRange[1]}</Typography>
            </Box>

            {/* Category Filter */}
            {distinctCategories.length > 0 && (
              <>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5, color: '#fff' }}>Category</Typography>
                <RadioGroup value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} sx={{ mb: 3 }}>
                  <FormControlLabel value="all" control={<Radio size="small" />} label="All Categories" />
                  {distinctCategories.map(cat => (
                    <FormControlLabel key={cat} value={cat} control={<Radio size="small" />} label={cat} />
                  ))}
                </RadioGroup>
              </>
            )}

            {/* Brand Filter */}
            {distinctBrands.length > 0 && (
              <>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, color: '#fff' }}>Brand</Typography>
                <FormGroup sx={{ mb: 3 }}>
                  {distinctBrands.map(brand => (
                    <FormControlLabel
                      key={brand}
                      control={
                        <Checkbox 
                          size="small" 
                          checked={selectedBrands.includes(brand)} 
                          onChange={() => handleBrandChange(brand)} 
                        />
                      }
                      label={brand}
                    />
                  ))}
                </FormGroup>
              </>
            )}

            {/* Rating Filter */}
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5, color: '#fff' }}>Minimum Rating</Typography>
            <RadioGroup value={minRating.toString()} onChange={(e) => setMinRating(parseFloat(e.target.value))} sx={{ mb: 1 }}>
              <FormControlLabel value="0" control={<Radio size="small" />} label="Any Rating" />
              <FormControlLabel value="4" control={<Radio size="small" />} label="4.0 ★ & Above" />
              <FormControlLabel value="3" control={<Radio size="small" />} label="3.0 ★ & Above" />
            </RadioGroup>

          </Paper>
        </Grid>

        {/* Results Grid */}
        <Grid item xs={12} md={9}>
          {filteredResults.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 8, backgroundColor: '#15171e', borderRadius: 4, border: '1px solid #2c2f3a' }}>
              <Typography variant="h6" sx={{ color: '#9aa0a6' }}>No products match your filters.</Typography>
              <Typography variant="body2" sx={{ color: '#9aa0a6', mt: 1 }}>Try adjusting the price slider or selecting another brand.</Typography>
            </Box>
          ) : (
            <Grid container spacing={3}>
              {filteredResults.map((card, idx) => (
                <Grid item xs={12} sm={6} md={4} key={card.product.id || idx}>
                  <ExplainableRankCard
                    product={card.product}
                    relevanceScore={card.relevance_score}
                    finalRankScore={card.final_rank_score}
                    featureContributions={card.feature_contributions}
                    onViewDetails={handleProductView}
                    onCartAdd={handleCartAddWithLogging}
                  />
                </Grid>
              ))}
            </Grid>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};
