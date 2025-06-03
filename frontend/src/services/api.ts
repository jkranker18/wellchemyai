import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

export interface ChatResponse {
  success: boolean;
  message: string;
  data: {
    response: string;
    user_id?: string;
  };
}

export const api = {
  async chat(message: string, userId?: string): Promise<ChatResponse> {
    const response = await axios.post<ChatResponse>(`${API_BASE_URL}/chat`, {
      message: message,
      user_id: userId
    });
    return response.data;
  },

  async user(message: string, context?: any): Promise<ChatResponse> {
    const response = await axios.post<ChatResponse>(`${API_BASE_URL}/user`, {
      message,
      context
    });
    return response.data;
  },

  async dietary(message: string, dietaryData?: any, healthContext?: any): Promise<ChatResponse> {
    const response = await axios.post<ChatResponse>(`${API_BASE_URL}/dietary`, {
      message,
      dietary_data: dietaryData,
      health_context: healthContext
    });
    return response.data;
  },
}; 