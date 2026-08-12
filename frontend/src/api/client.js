import axios from "axios";

// Determine the base API URL (default to local FastAPI server)
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Axios Request Interceptor: Attach authorization token if present
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Axios Response Interceptor: Handle global errors (e.g. 401/403/500)
export const setupResponseInterceptors = (onLogout) => {
  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response) {
        const { status } = error.response;
        if (status === 401) {
          // Token expired or invalid
          onLogout();
        }
      }
      return Promise.reject(error);
    }
  );
};

export default apiClient;
