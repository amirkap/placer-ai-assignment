import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Typography,
  Box,
  Alert,
  AppBar,
  Toolbar,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Tabs,
  Tab,
} from '@mui/material';
import { Analytics as AnalyticsIcon, TableChart, TrendingUp } from '@mui/icons-material';
import StatsCards from './StatsCards';
import POIFilters from './POIFilters';
import POITable from './POITable';
import Analytics from './Analytics';
import { poiApi } from '../services/api';
import {
  PaginatedPOIResponse,
  SummaryStats,
  Filters,
  FilterOptions,
} from '../types/poi';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1976d2',
        },
      },
    },
  },
});

const Dashboard: React.FC = () => {
  const [poiData, setPOIData] = useState<PaginatedPOIResponse | null>(null);
  const [summaryStats, setSummaryStats] = useState<SummaryStats | null>(null);
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({
    chains: [],
    dmas: [],
    categories: [],
    cities: [],
    states: [],
  });
  const [filters, setFilters] = useState<Filters>({});
  const [page, setPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  // Load filter options on mount
  useEffect(() => {
    const loadFilterOptions = async () => {
      try {
        const options = await poiApi.getFilterOptions();
        setFilterOptions(options);
      } catch (err) {
        console.error('Error loading filter options:', err);
        setError('Failed to load filter options');
      }
    };

    loadFilterOptions();
  }, []);

  // Load POI data
  const loadPOIData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await poiApi.getPOIs(page, rowsPerPage, filters);
      setPOIData(data);
    } catch (err) {
      console.error('Error loading POI data:', err);
      setError('Failed to load POI data');
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, filters]);

  // Load summary stats
  const loadSummaryStats = useCallback(async () => {
    setStatsLoading(true);
    try {
      const stats = await poiApi.getSummaryStats(filters);
      setSummaryStats(stats);
    } catch (err) {
      console.error('Error loading summary stats:', err);
      setError('Failed to load summary statistics');
    } finally {
      setStatsLoading(false);
    }
  }, [filters]);

  // Load data when dependencies change
  useEffect(() => {
    loadPOIData();
  }, [loadPOIData]);

  useEffect(() => {
    loadSummaryStats();
  }, [loadSummaryStats]);

  const handleFiltersChange = (newFilters: Filters) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page when filters change
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (newRowsPerPage: number) => {
    setRowsPerPage(newRowsPerPage);
    setPage(1); // Reset to first page when page size changes
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <AnalyticsIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Placer.ai POI Analytics Dashboard
          </Typography>
          <Typography variant="body2">
            Big Box Stores - October 2023
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Summary Statistics */}
        {summaryStats && (
          <StatsCards stats={summaryStats} loading={statsLoading} />
        )}

        {/* Filters */}
        <POIFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          filterOptions={filterOptions}
        />

        {/* Navigation Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="dashboard tabs">
            <Tab icon={<TableChart />} label="POI Data" />
            <Tab icon={<TrendingUp />} label="Analytics" />
          </Tabs>
        </Box>

        {/* Tab Content */}
        {activeTab === 0 && (
          <Box>
            <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
              Point of Interest Data
            </Typography>
            
            <POITable
              data={poiData}
              loading={loading}
              onPageChange={handlePageChange}
              onRowsPerPageChange={handleRowsPerPageChange}
            />
          </Box>
        )}

        {activeTab === 1 && (
          <Analytics filters={filters} />
        )}

        {/* Footer */}
        <Box sx={{ mt: 4, py: 3, textAlign: 'center', borderTop: '1px solid #e0e0e0' }}>
          <Typography variant="body2" color="text.secondary">
            Placer.ai POI Analytics Dashboard - Built with React & FastAPI
          </Typography>
        </Box>
      </Container>
    </ThemeProvider>
  );
};

export default Dashboard;
