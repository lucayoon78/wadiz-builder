/**
 * API Client for Wadiz Page Builder
 */
import axios, { AxiosInstance } from 'axios';
import type {
  User,
  AuthTokens,
  Project,
  Image,
  AIGenerateRequest,
  AIGenerateResponse,
  Template,
  HTMLExportResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_V1 = `${API_BASE_URL}/api/v1`;

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_V1,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle 401 errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // ===== Auth =====
  async register(email: string, password: string, full_name?: string): Promise<User> {
    const { data } = await this.client.post('/auth/register', {
      email,
      password,
      full_name,
    });
    return data;
  }

  async login(email: string, password: string): Promise<AuthTokens> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const { data } = await this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    localStorage.setItem('access_token', data.access_token);
    return data;
  }

  async getCurrentUser(): Promise<User> {
    const { data } = await this.client.get('/auth/me');
    return data;
  }

  logout() {
    localStorage.removeItem('access_token');
  }

  // ===== Projects =====
  async createProject(projectData: Partial<Project>): Promise<Project> {
    const { data } = await this.client.post('/projects/', projectData);
    return data;
  }

  async getProjects(skip = 0, limit = 20): Promise<Project[]> {
    const { data } = await this.client.get('/projects/', {
      params: { skip, limit },
    });
    return data;
  }

  async getProject(id: number): Promise<Project> {
    const { data } = await this.client.get(`/projects/${id}`);
    return data;
  }

  async updateProject(id: number, updates: Partial<Project>): Promise<Project> {
    const { data } = await this.client.patch(`/projects/${id}`, updates);
    return data;
  }

  async deleteProject(id: number): Promise<void> {
    await this.client.delete(`/projects/${id}`);
  }

  // ===== Images =====
  async uploadImages(
    projectId: number,
    files: File[],
    section: 'intro' | 'body' | 'outro' = 'body'
  ): Promise<Image[]> {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    formData.append('section', section);

    const { data } = await this.client.post(`/images/upload/${projectId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  }

  async getProjectImages(projectId: number): Promise<Image[]> {
    const { data } = await this.client.get(`/images/project/${projectId}`);
    return data;
  }

  async deleteImage(id: number): Promise<void> {
    await this.client.delete(`/images/${id}`);
  }

  async reorderImage(id: number, newPosition: number): Promise<Image> {
    const formData = new FormData();
    formData.append('new_position', newPosition.toString());

    const { data } = await this.client.patch(`/images/${id}/reorder`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  }

  // ===== AI Generation =====
  async generateWadizPage(request: AIGenerateRequest): Promise<AIGenerateResponse> {
    const { data } = await this.client.post('/ai/generate', request);
    return data;
  }

  async regenerateAlternatives(projectId: number): Promise<AIGenerateResponse> {
    const { data } = await this.client.post(`/ai/regenerate-alternatives/${projectId}`);
    return data;
  }

  async applyAlternative(projectId: number, alternativeIndex: number): Promise<Project> {
    const { data } = await this.client.post(
      `/ai/apply-alternative/${projectId}/${alternativeIndex}`
    );
    return data;
  }

  // ===== Templates =====
  async getTemplates(category?: string, skip = 0, limit = 20): Promise<Template[]> {
    const { data } = await this.client.get('/templates/', {
      params: { category, skip, limit },
    });
    return data;
  }

  async getTemplate(id: number): Promise<Template> {
    const { data } = await this.client.get(`/templates/${id}`);
    return data;
  }

  // ===== Export =====
  async exportHTML(projectId: number, templateId?: number): Promise<HTMLExportResponse> {
    const { data } = await this.client.post('/export/html', {
      project_id: projectId,
      template_id: templateId,
    });
    return data;
  }

  async downloadHTML(fileKey: string): Promise<Blob> {
    const { data } = await this.client.get(`/export/download/${fileKey}`, {
      responseType: 'blob',
    });
    return data;
  }
}

export const api = new APIClient();
