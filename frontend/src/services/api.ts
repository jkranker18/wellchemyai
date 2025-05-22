const API_BASE_URL = 'http://localhost:5000';

export interface ChatResponse {
  success: boolean;
  message: string;
  data: {
    response: string;
  };
}

export const api = {
  async chat(message: string): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
    return response.json();
  },

  async user(message: string, context?: any): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/user`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, context }),
    });
    return response.json();
  },

  async dietary(message: string, dietaryData?: any, healthContext?: any): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/dietary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, dietary_data: dietaryData, health_context: healthContext }),
    });
    return response.json();
  },
}; 