import axios from 'axios';
import { PaginatedPOIResponse, SummaryStats, Filters, FilterOptions } from '../types/poi';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const poiApi = {
  async getPOIs(
    page: number = 1,
    limit: number = 20,
    filters: Filters = {}
  ): Promise<PaginatedPOIResponse> {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('limit', limit.toString());
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await api.get(`/api/v1/pois?${params.toString()}`);
    return response.data;
  },

  async getSummaryStats(filters: Filters = {}): Promise<SummaryStats> {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await api.get(`/api/v1/pois/summary?${params.toString()}`);
    return response.data;
  },

  async getFilterOptions(): Promise<FilterOptions> {
    const [chains, dmas, categories, cities, states] = await Promise.all([
      api.get('/api/v1/pois/filters/chains'),
      api.get('/api/v1/pois/filters/dmas'),
      api.get('/api/v1/pois/filters/categories'),
      api.get('/api/v1/pois/filters/cities'),
      api.get('/api/v1/pois/filters/states'),
    ]);

    return {
      chains: chains.data.chains,
      dmas: dmas.data.dmas,
      categories: categories.data.categories,
      cities: cities.data.cities,
      states: states.data.states,
    };
  },

  async getAutocomplete(query: string, field?: string): Promise<string[]> {
    const params = new URLSearchParams();
    params.append('query', query);
    if (field) {
      params.append('field', field);
    }

    const response = await api.get(`/api/v1/pois/autocomplete?${params.toString()}`);
    return response.data.suggestions;
  },
};
