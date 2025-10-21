import { toast } from "@/hooks/use-toast";
import { useAuthStore } from '@/store/authStore';
import axios from 'axios';

export interface Note {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  is_pinned: boolean;
  category: number | null;
}

export interface Category {
  id: number;
  name: string;
  user: number;
}

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1'
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
  
  // Add response interceptor
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        useAuthStore.getState().logout();
        
        toast({
          variant: "destructive",
          title: "Session Expired",
          description: "Your session has expired. Please log in again.",
        });
  
        setTimeout(() => {
          window.location.href = '/login';
        }, 1500);
      }
      return Promise.reject(error);
    }
  );

// Notes API
export const getNotes = async (page: number = 1, pageSize: number = 20): Promise<{results: Note[], count: number, next: string | null, previous: string | null}> => {
  const response = await api.get(`/notes/?page=${page}&page_size=${pageSize}`);
  return response.data;
};

export const createNote = async (data: { title: string; content: string; category?: number | null }): Promise<Note> => {
  const response = await api.post('/notes/', data);
  return response.data;
};

export const updateNote = async (id: number, data: { title: string; content: string; category?: number | null }): Promise<Note> => {
  const response = await api.put(`/notes/${id}/`, data);
  return response.data;
};

export const deleteNote = async (id: number): Promise<void> => {
  await api.delete(`/notes/${id}/`);
};

export const togglePinNote = async (id: number, isPinned: boolean): Promise<Note> => {
    const response = await api.patch(`/notes/${id}/`, { is_pinned: isPinned });
    return response.data;
  };

// Categories API
export const getCategories = async (): Promise<{results: Category[], count: number}> => {
  const response = await api.get('/categories/');
  return response.data;
};

export const createCategory = async (name: string): Promise<Category> => {
  const response = await api.post('/categories/', { name });
  return response.data;
};

export const deleteCategory = async (id: number): Promise<void> => {
    await api.delete(`/categories/${id}/`);
};

export default api;