import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Chip,
  Grid,
  Autocomplete,
  Paper,
  Typography,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { Filters, FilterOptions } from '../types/poi';
import { poiApi } from '../services/api';

interface POIFiltersProps {
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
  filterOptions: FilterOptions;
}

const POIFilters: React.FC<POIFiltersProps> = ({
  filters,
  onFiltersChange,
  filterOptions,
}) => {
  const [autocompleteOptions, setAutocompleteOptions] = useState<string[]>([]);
  const [searchValue, setSearchValue] = useState(filters.search || '');

  useEffect(() => {
    setSearchValue(filters.search || '');
  }, [filters.search]);

  const handleFilterChange = (key: keyof Filters, value: any) => {
    const newFilters = { ...filters };
    if (value === '' || value === null || value === undefined) {
      delete newFilters[key];
    } else {
      newFilters[key] = value;
    }
    onFiltersChange(newFilters);
  };

  const handleSearchChange = async (value: string) => {
    setSearchValue(value);
    if (value.length >= 2) {
      try {
        const suggestions = await poiApi.getAutocomplete(value);
        setAutocompleteOptions(suggestions);
      } catch (error) {
        console.error('Error fetching autocomplete suggestions:', error);
      }
    } else {
      setAutocompleteOptions([]);
    }
  };

  const handleSearchSubmit = () => {
    handleFilterChange('search', searchValue);
  };

  const clearAllFilters = () => {
    setSearchValue('');
    onFiltersChange({});
  };

  const getActiveFiltersCount = () => {
    return Object.keys(filters).length;
  };

  return (
    <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <FilterIcon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6" component="h2">
          Filters
        </Typography>
        {getActiveFiltersCount() > 0 && (
          <Chip
            label={`${getActiveFiltersCount()} active`}
            color="primary"
            size="small"
            sx={{ ml: 1 }}
          />
        )}
      </Box>

      <Grid container spacing={2}>
        {/* Search */}
        <Grid item xs={12} md={6}>
          <Autocomplete
            freeSolo
            value={searchValue}
            options={autocompleteOptions}
            onInputChange={(_, value) => handleSearchChange(value)}
            renderInput={(params) => (
              <TextField
                {...params}
                fullWidth
                label="Search POIs"
                placeholder="Search by name, chain, city, address..."
                InputProps={{
                  ...params.InputProps,
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />,
                }}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSearchSubmit();
                  }
                }}
              />
            )}
          />
          <Button
            variant="contained"
            onClick={handleSearchSubmit}
            sx={{ mt: 1, mr: 1 }}
            size="small"
          >
            Search
          </Button>
          {searchValue && (
            <Button
              variant="outlined"
              onClick={() => {
                setSearchValue('');
                handleFilterChange('search', '');
              }}
              sx={{ mt: 1 }}
              size="small"
              startIcon={<ClearIcon />}
            >
              Clear Search
            </Button>
          )}
        </Grid>

        {/* Chain Name */}
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Chain</InputLabel>
            <Select
              value={filters.chain_name || ''}
              label="Chain"
              onChange={(e) => handleFilterChange('chain_name', e.target.value)}
            >
              <MenuItem value="">All Chains</MenuItem>
              {filterOptions.chains.map((chain) => (
                <MenuItem key={chain} value={chain}>
                  {chain}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* Category */}
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Category</InputLabel>
            <Select
              value={filters.sub_category || ''}
              label="Category"
              onChange={(e) => handleFilterChange('sub_category', e.target.value)}
            >
              <MenuItem value="">All Categories</MenuItem>
              {filterOptions.categories.map((category) => (
                <MenuItem key={category} value={category}>
                  {category}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* DMA */}
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>DMA</InputLabel>
            <Select
              value={filters.dma || ''}
              label="DMA"
              onChange={(e) => handleFilterChange('dma', e.target.value)}
            >
              <MenuItem value="">All DMAs</MenuItem>
              {filterOptions.dmas.map((dma) => (
                <MenuItem key={dma} value={dma}>
                  {dma}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* City */}
        <Grid item xs={12} sm={6} md={3}>
          <Autocomplete
            value={filters.city || ''}
            options={filterOptions.cities}
            onChange={(_, value) => handleFilterChange('city', value)}
            renderInput={(params) => (
              <TextField {...params} label="City" placeholder="Select city" />
            )}
          />
        </Grid>

        {/* State */}
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>State</InputLabel>
            <Select
              value={filters.state_code || ''}
              label="State"
              onChange={(e) => handleFilterChange('state_code', e.target.value)}
            >
              <MenuItem value="">All States</MenuItem>
              {filterOptions.states.map((state) => (
                <MenuItem key={state} value={state}>
                  {state}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* Open/Closed Status */}
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.is_open === undefined ? '' : filters.is_open.toString()}
              label="Status"
              onChange={(e) => {
                const value = e.target.value;
                if (value === '') {
                  handleFilterChange('is_open', undefined);
                } else {
                  handleFilterChange('is_open', value === 'true');
                }
              }}
            >
              <MenuItem value="">All Venues</MenuItem>
              <MenuItem value="true">Open Only</MenuItem>
              <MenuItem value="false">Closed Only</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {/* Clear All Filters */}
        <Grid item xs={12} sm={6} md={3}>
          <Button
            variant="outlined"
            color="secondary"
            fullWidth
            onClick={clearAllFilters}
            startIcon={<ClearIcon />}
            disabled={getActiveFiltersCount() === 0}
            sx={{ height: '56px' }}
          >
            Clear All Filters
          </Button>
        </Grid>
      </Grid>

      {/* Active Filters Display */}
      {getActiveFiltersCount() > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Active Filters:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {Object.entries(filters).map(([key, value]) => (
              <Chip
                key={key}
                label={`${key}: ${value}`}
                onDelete={() => handleFilterChange(key as keyof Filters, undefined)}
                color="primary"
                variant="outlined"
                size="small"
              />
            ))}
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default POIFilters;
