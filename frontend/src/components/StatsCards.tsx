import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Chip,
} from '@mui/material';
import {
  Store as StoreIcon,
  Timeline as TimelineIcon,
  AttachMoney as MoneyIcon,
  Schedule as ScheduleIcon,
  CheckCircle as OpenIcon,
  Cancel as ClosedIcon,
  Business as ChainIcon,
  LocationOn as LocationIcon,
} from '@mui/icons-material';
import { SummaryStats } from '../types/poi';

interface StatsCardsProps {
  stats: SummaryStats;
  loading?: boolean;
}

const StatsCards: React.FC<StatsCardsProps> = ({ stats, loading = false }) => {
  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toLocaleString();
  };

  const formatCurrency = (amount: number): string => {
    if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(1)}K`;
    }
    return `$${amount.toLocaleString()}`;
  };

  const statsConfig = [
    {
      title: 'Total Venues',
      value: formatNumber(stats.total_venues),
      icon: <StoreIcon />,
      color: '#1976d2',
    },
    {
      title: 'Total Foot Traffic',
      value: formatNumber(stats.total_foot_traffic),
      icon: <TimelineIcon />,
      color: '#388e3c',
    },
    {
      title: 'Total Sales',
      value: formatCurrency(stats.total_sales),
      icon: <MoneyIcon />,
      color: '#f57c00',
    },
    {
      title: 'Avg Dwell Time',
      value: `${stats.avg_dwell_time.toFixed(1)} min`,
      icon: <ScheduleIcon />,
      color: '#7b1fa2',
    },
    {
      title: 'Open Venues',
      value: formatNumber(stats.open_venues),
      icon: <OpenIcon />,
      color: '#2e7d32',
    },
    {
      title: 'Closed Venues',
      value: formatNumber(stats.closed_venues),
      icon: <ClosedIcon />,
      color: '#d32f2f',
    },
    {
      title: 'Unique Chains',
      value: formatNumber(stats.unique_chains),
      icon: <ChainIcon />,
      color: '#1565c0',
    },
    {
      title: 'Unique DMAs',
      value: formatNumber(stats.unique_dmas),
      icon: <LocationIcon />,
      color: '#5e35b1',
    },
  ];

  if (loading) {
    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {Array.from({ length: 8 }).map((_, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 1,
                      bgcolor: 'grey.200',
                      mr: 2,
                    }}
                  />
                  <Typography variant="h6" component="div" sx={{ color: 'grey.400' }}>
                    Loading...
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Loading...
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  return (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      {statsConfig.map((stat, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Card sx={{ height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 40,
                    height: 40,
                    borderRadius: 1,
                    bgcolor: `${stat.color}20`,
                    color: stat.color,
                    mr: 2,
                  }}
                >
                  {stat.icon}
                </Box>
                <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
                  {stat.value}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                {stat.title}
              </Typography>
              {(stat.title === 'Open Venues' || stat.title === 'Closed Venues') && (
                <Box sx={{ mt: 1 }}>
                  <Chip
                    size="small"
                    label={stat.title === 'Open Venues' ? 'Active' : 'Inactive'}
                    color={stat.title === 'Open Venues' ? 'success' : 'error'}
                    variant="outlined"
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default StatsCards;
