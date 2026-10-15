import { create } from 'zustand';

interface SearchState {
  globalQuery: string;
  setGlobalQuery: (query: string) => void;
  clearGlobalQuery: () => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  globalQuery: '',
  setGlobalQuery: (query: string) => set({ globalQuery: query }),
  clearGlobalQuery: () => set({ globalQuery: '' }),
}));
