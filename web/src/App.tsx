import {  ChakraProvider, useToast } from '@chakra-ui/react'
import { HelmetProvider } from 'react-helmet-async'

import { Font, theme } from '@theme/config'
import Router from '@routes/index'
import 'chartjs-adapter-luxon';

import {
    Chart as ChartJS,
    registerables
} from 'chart.js';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect, useMemo } from 'react';


ChartJS.register(
    ...registerables
);



export default function App() {
    const toast = useToast();

    const queryClient = useMemo(()=>new QueryClient({
        defaultOptions: {
            queries: {
                refetchOnWindowFocus: false,
                retry: 3
            }
        },
    }), []);

    useEffect(() => {
        // Listen for the 'error' event on the queryCache
        const unsubscribe = queryClient.getQueryCache().subscribe(({query}) => {
          if (query.state.error) {
            toast({
                title: 'Ups! Something went wrong.',
                description: "Please retry or refresh the page. If the problem persists, please contact support.",
                status: 'error',
                duration: 5000,
                isClosable: true,
                position: "top-right"
            });
            console.error('Error fetching data', query.state.error);
          }
        });
    
        // Clean up the subscription
        return () => unsubscribe();
      }, [queryClient]);

    return (
        <HelmetProvider>
            <QueryClientProvider client={queryClient}>
                <ChakraProvider theme={theme}>
                    <Font />
                    <Router />
                </ChakraProvider>
            </QueryClientProvider>
        </HelmetProvider>
    )
}
