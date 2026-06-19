const API_BASE_URL = 'http://localhost:8000/api/auths';

type LoginTokens = {
  access?: string;
  refresh?: string;
};

export const getApiBaseUrl = () => API_BASE_URL;

export const saveTokens = (tokens: LoginTokens) => {
  if (tokens.access) {
    localStorage.setItem('access_token', tokens.access);
  }

  if (tokens.refresh) {
    localStorage.setItem('refresh_token', tokens.refresh);
  }
};

export const getAccessToken = () => localStorage.getItem('access_token');
