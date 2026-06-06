import React, { useState, useEffect } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  InputBase, 
  Box, 
  IconButton, 
  Badge, 
  Button, 
  Menu, 
  MenuItem, 
  Autocomplete, 
  TextField 
} from '@mui/material';
import { Search, Compass, BarChart2, User, Camera, ShoppingCart } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { searchAPI } from '../services/api';

interface NavbarProps {
  sessionId: string;
  cartCount: number;
  onTextSearch: (query: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ sessionId, cartCount, onTextSearch }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  
  // Fetch autocomplete suggestions
  useEffect(() => {
    if (searchQuery.length < 2) {
      setSuggestions([]);
      return;
    }
    const delayDebounceFn = setTimeout(async () => {
      try {
        const list = await searchAPI.autocomplete(searchQuery);
        setSuggestions(list);
      } catch (e) {
        console.error(e);
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  const handleSearchSubmit = (queryStr: string) => {
    if (queryStr.trim()) {
      onTextSearch(queryStr);
      navigate('/results');
    }
  };

  const handleProfileClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileClose = () => {
    setAnchorEl(null);
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <AppBar position="sticky" sx={{ backgroundColor: '#15171e', borderBottom: '1px solid #2c2f3a', boxShadow: 'none' }}>
      <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', gap: 2 }}>
        
        {/* Logo */}
        <Typography 
          variant="h6" 
          onClick={() => navigate('/')}
          sx={{ 
            fontFamily: 'Outfit', 
            fontWeight: 800, 
            background: 'linear-gradient(45deg, #757de8, #ff4081)', 
            WebkitBackgroundClip: 'text', 
            WebkitTextFillColor: 'transparent',
            cursor: 'pointer',
            fontSize: '1.4rem'
          }}
        >
          ShopLens AI
        </Typography>

        {/* Autocomplete Input */}
        <Box sx={{ flexGrow: 1, maxWith: 600, mx: 2, position: 'relative' }}>
          <Autocomplete
            freeSolo
            options={suggestions}
            inputValue={searchQuery}
            onInputChange={(_, value) => setSearchQuery(value)}
            onChange={(_, value) => value && handleSearchSubmit(value as string)}
            renderInput={(params) => (
              <TextField
                {...params}
                size="small"
                placeholder="Search products by brand, color, category..."
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSearchSubmit(searchQuery);
                  }
                }}
                InputProps={{
                  ...params.InputProps,
                  startAdornment: <Search size={16} style={{ color: '#9aa0a6', marginRight: 8 }} />,
                  style: { 
                    color: '#fff', 
                    backgroundColor: '#0d0e12', 
                    borderRadius: 20, 
                    border: '1px solid #2c2f3a',
                    paddingLeft: 12
                  }
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    '& fieldset': { border: 'none' }
                  }
                }}
              />
            )}
          />
        </Box>

        {/* Navigation Links */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Button 
            startIcon={<Compass size={16} />}
            onClick={() => navigate('/recommendations')}
            sx={{ 
              color: isActive('/recommendations') ? '#757de8' : '#9aa0a6', 
              textTransform: 'none', 
              fontWeight: 600,
              '&:hover': { color: '#fff' }
            }}
          >
            Personal Feed
          </Button>

          <Button 
            startIcon={<BarChart2 size={16} />}
            onClick={() => navigate('/admin')}
            sx={{ 
              color: isActive('/admin') ? '#757de8' : '#9aa0a6', 
              textTransform: 'none', 
              fontWeight: 600,
              '&:hover': { color: '#fff' }
            }}
          >
            Admin Panel
          </Button>

          {/* Cart Icon */}
          <IconButton sx={{ color: '#9aa0a6' }}>
            <Badge badgeContent={cartCount} color="secondary">
              <ShoppingCart size={20} />
            </Badge>
          </IconButton>

          {/* Profile Menu */}
          <IconButton onClick={handleProfileClick} sx={{ color: '#fff', border: '1px solid #2c2f3a', p: 0.8 }}>
            <User size={18} />
          </IconButton>
          
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileClose}
            PaperProps={{
              sx: { backgroundColor: '#15171e', border: '1px solid #2c2f3a', color: '#fff' }
            }}
          >
            <MenuItem onClick={() => { handleProfileClose(); navigate('/admin'); }}>Admin Dashboard</MenuItem>
            <MenuItem onClick={handleProfileClose}>Logout</MenuItem>
          </Menu>
        </Box>
        
      </Toolbar>
    </AppBar>
  );
};
