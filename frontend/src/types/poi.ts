export interface POI {
  entity_id: string;
  name: string;
  chain_name: string;
  sub_category: string;
  dma: number | null;
  city: string;
  state_name: string;
  foot_traffic: number;
  is_open: boolean;
  sales: number;
  avg_dwell_time_min: number;
  area_sqft: number;
  ft_per_sqft: number;
  street_address: string;
  postal_code: string;
  date_opened: string | null;
  date_closed: string | null;
}

export interface PaginatedPOIResponse {
  items: POI[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface SummaryStats {
  total_venues: number;
  total_foot_traffic: number;
  total_sales: number;
  avg_dwell_time: number;
  open_venues: number;
  closed_venues: number;
  unique_chains: number;
  unique_dmas: number;
}

export interface Filters {
  chain_name?: string;
  dma?: number;
  sub_category?: string;
  city?: string;
  state_code?: string;
  is_open?: boolean;
  search?: string;
}

export interface FilterOptions {
  chains: string[];
  dmas: number[];
  categories: string[];
  cities: string[];
  states: string[];
}
