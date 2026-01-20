export const API_BASE = typeof window === 'undefined'
    ? (process.env.INTERNAL_API_URL || 'http://127.0.0.1:8000')
    : '';
