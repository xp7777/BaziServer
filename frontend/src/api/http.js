import axios from 'axios'; const http = axios.create({ baseURL: 'http://localhost:5000', timeout: 60000, headers: { 'Content-Type': 'application/json' } }); export default http;
