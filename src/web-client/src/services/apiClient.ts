import axios, { type AxiosInstance } from 'axios'

const apiUrl: string = import.meta.env.VITE_API_BASE_URL

const apiClient: AxiosInstance = axios.create({
  baseURL: apiUrl,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

export default apiClient
