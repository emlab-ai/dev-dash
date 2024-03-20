import axios from 'axios';

// Create an instance of axios with predefined configurations
export const backendClient = axios.create({
  timeout: 3000, // request timeout
  headers: {'X-Custom-Header': 'foobar'} // any custom headers
});