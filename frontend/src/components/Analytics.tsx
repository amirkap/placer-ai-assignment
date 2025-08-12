import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Alert,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';
import { poiApi } from '../services/api';
import { Filters } from '../types/poi';

interface AnalyticsProps {
  filters: Filters;
}

interface ChainPerformance {
  chain_name: string;
  total_venues: number;
  total_foot_traffic: number;
  total_sales: number;
  avg_sales_per_visitor: number;
  open_venues: number;
  closed_venues: number;
}

interface DMADistribution {
  dma: number;
  venue_count: number;
  total_foot_traffic: number;
  total_sales: number;
  unique_chains: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658'];

const Analytics: React.FC<AnalyticsProps> = ({ filters }) => {
  const [chainData, setChainData] = useState<ChainPerformance[]>([]);
  const [dmaData, setDMAData] = useState<DMADistribution[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [chainResponse, dmaResponse] = await Promise.all([
        fetch('/api/v1/pois/analytics/chain-performance'),
        fetch('/api/v1/pois/analytics/dma-distribution'),
      ]);

      if (!chainResponse.ok || !dmaResponse.ok) {
        throw new Error('Failed to load analytics data');
      }

      const chainResult = await chainResponse.json();
      const dmaResult = await dmaResponse.json();

      setChainData(chainResult.chain_performance);
      setDMAData(dmaResult.dma_distribution);
    } catch (err) {
      console.error('Error loading analytics:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };



  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toLocaleString();
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Loading analytics...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <AnalyticsIcon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h5" component="h2">
          Analytics & Insights
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Chain Performance Chart */}
        <Grid item xs={12} lg={8}>
          <Paper elevation={1} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Chain Performance - Foot Traffic vs Sales
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={chainData.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="chain_name" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis yAxisId="left" orientation="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip 
                  formatter={(value, name) => [
                    typeof value === 'number' ? formatNumber(value) : value,
                    name
                  ]}
                />
                <Legend />
                <Bar 
                  yAxisId="left" 
                  dataKey="total_foot_traffic" 
                  fill="#8884d8" 
                  name="Foot Traffic"
                />
                <Bar 
                  yAxisId="right" 
                  dataKey="total_sales" 
                  fill="#82ca9d" 
                  name="Sales ($)"
                />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* DMA Distribution Pie Chart */}
        <Grid item xs={12} lg={4}>
          <Paper elevation={1} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Top DMAs by Venue Count
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={dmaData.slice(0, 7)}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ dma, venue_count }) => `DMA ${dma}: ${venue_count}`}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="venue_count"
                >
                  {dmaData.slice(0, 7).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [formatNumber(Number(value)), 'Venues']} />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Sales per Visitor by Chain */}
        <Grid item xs={12}>
          <Paper elevation={1} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Average Sales per Visitor by Chain
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chainData.slice(0, 8)} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="chain_name" type="category" width={80} />
                <Tooltip 
                  formatter={(value) => [`$${Number(value).toFixed(2)}`, 'Sales per Visitor']}
                />
                <Bar dataKey="avg_sales_per_visitor" fill="#ff7300" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
