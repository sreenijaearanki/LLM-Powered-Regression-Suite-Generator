const RENDER_BACKEND = 'https://llm-regression-suite-backend.onrender.com'
const LOCAL_BACKEND  = 'http://localhost:8000'

export const API_BASE = window.location.hostname === 'localhost'
  ? LOCAL_BACKEND
  : RENDER_BACKEND
