import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Typography,
  Box,
  TablePagination,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle as OpenIcon,
  Cancel as ClosedIcon,
  LocationOn as LocationIcon,
} from '@mui/icons-material';
import { POI, PaginatedPOIResponse } from '../types/poi';

interface POITableProps {
  data: PaginatedPOIResponse | null;
  loading: boolean;
  onPageChange: (page: number) => void;
  onRowsPerPageChange: (rowsPerPage: number) => void;
}

const POITable: React.FC<POITableProps> = ({
  data,
  loading,
  onPageChange,
  onRowsPerPageChange,
}) => {
  const formatNumber = (num: number): string => {
    return num.toLocaleString();
  };

  const formatCurrency = (amount: number): string => {
    return `$${amount.toLocaleString()}`;
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    onPageChange(newPage + 1); // API uses 1-based pagination
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    onRowsPerPageChange(parseInt(event.target.value, 10));
    onPageChange(1); // Reset to first page
  };

  if (loading) {
    return (
      <Paper elevation={1}>
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      </Paper>
    );
  }

  if (!data || data.items.length === 0) {
    return (
      <Paper elevation={1}>
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            No POI data found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your filters or search criteria
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper elevation={1}>
      <TableContainer>
        <Table sx={{ minWidth: 650 }} aria-label="POI table">
          <TableHead>
            <TableRow sx={{ backgroundColor: 'grey.50' }}>
              <TableCell sx={{ fontWeight: 'bold' }}>Name</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Chain</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Category</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Location</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }} align="right">DMA</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }} align="right">Foot Traffic</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }} align="right">Sales</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }} align="right">Dwell Time</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }} align="center">Status</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Dates</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.items.map((poi: POI) => (
              <TableRow
                key={poi.entity_id}
                sx={{
                  '&:nth-of-type(odd)': { backgroundColor: 'action.hover' },
                  '&:hover': { backgroundColor: 'action.selected' },
                }}
              >
                <TableCell>
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                      {poi.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {poi.street_address}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={poi.chain_name}
                    size="small"
                    variant="outlined"
                    color="primary"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={poi.sub_category}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <LocationIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                    <Box>
                      <Typography variant="body2">
                        {poi.city}, {poi.state_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {poi.postal_code}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell align="right">
                  {poi.dma || 'N/A'}
                </TableCell>
                <TableCell align="right">
                  <Tooltip title={`${formatNumber(poi.foot_traffic)} visits`}>
                    <Typography variant="body2">
                      {formatNumber(poi.foot_traffic)}
                    </Typography>
                  </Tooltip>
                  <Typography variant="caption" color="text.secondary">
                    {poi.ft_per_sqft.toFixed(2)} per sqft
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2">
                    {formatCurrency(poi.sales)}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2">
                    {poi.avg_dwell_time_min.toFixed(1)} min
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Chip
                    icon={poi.is_open ? <OpenIcon /> : <ClosedIcon />}
                    label={poi.is_open ? 'Open' : 'Closed'}
                    color={poi.is_open ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="caption" display="block">
                      Opened: {formatDate(poi.date_opened)}
                    </Typography>
                    {poi.date_closed && (
                      <Typography variant="caption" display="block" color="error">
                        Closed: {formatDate(poi.date_closed)}
                      </Typography>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[10, 20, 50, 100]}
        component="div"
        count={data.total}
        rowsPerPage={data.limit}
        page={data.page - 1} // Convert to 0-based for MUI
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        showFirstButton
        showLastButton
      />
    </Paper>
  );
};

export default POITable;
