import { ChakraProvider } from '@chakra-ui/react'
import { HelmetProvider } from 'react-helmet-async'

import { Font, theme } from '@theme/config'
import Router from '@routes/index'
import 'chartjs-adapter-luxon';

import {
    Chart as ChartJS,
    registerables
} from 'chart.js';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';


ChartJS.register(
    ...registerables
);


const queryClient = new QueryClient();
export default function App() {

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
