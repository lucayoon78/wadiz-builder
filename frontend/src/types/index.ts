// Type definitions for Wadiz Page Builder

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface Project {
  id: number;
  user_id: number;
  title: string;
  slug: string;
  category?: string;
  product_name?: string;
  usp?: string;
  target_audience?: string;
  ai_copy?: string;
  ai_alternatives?: string[];
  page_structure?: PageStructure;
  is_published: boolean;
  created_at: string;
  updated_at: string;
  images: Image[];
}

export interface Image {
  id: number;
  project_id: number;
  filename: string;
  original_filename: string;
  file_url: string;
  file_size?: number;
  width?: number;
  height?: number;
  mime_type?: string;
  position: number;
  section: 'intro' | 'body' | 'outro';
  created_at: string;
}

export interface PageStructure {
  intro?: {
    hooking: string;
    image_guide?: string;
  };
  body?: BodySection[];
  outro?: {
    faq?: string[];
    cta?: string;
  };
}

export interface BodySection {
  title: string;
  subtitle?: string;
  description?: string;
  image_guide?: string;
}

export interface AIGenerateRequest {
  project_id: number;
  product_name: string;
  usp: string;
  target_audience: string;
  category?: string;
  additional_context?: string;
}

export interface AIGenerateResponse {
  main_copy: string;
  alternatives: string[];
  page_structure: PageStructure;
}

export interface Template {
  id: number;
  name: string;
  category?: string;
  description?: string;
  structure: any;
  usage_count: number;
  is_active: boolean;
  created_at: string;
}

export interface HTMLExportResponse {
  html_url: string;
  expires_at: string;
}
