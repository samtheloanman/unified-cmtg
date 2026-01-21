const isServer = typeof window === 'undefined';

export const API_BASE = isServer
    ? (process.env.INTERNAL_API_URL || 'http://127.0.0.1:8001')
    : '';
