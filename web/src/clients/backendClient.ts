import { useAuth } from '@src/providers/authProvider';
import axios from 'axios';
import { useMemo } from 'react';

export function useAxiosClient() {
  const { token } = useAuth();

  const client = useMemo(() => axios.create({
    timeout: 30000,
    headers: {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json'
    }
  }), [token]);

  return client;
}