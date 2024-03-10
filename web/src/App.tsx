import { ChakraProvider } from '@chakra-ui/react'
import { HelmetProvider } from 'react-helmet-async'

import { Font, theme } from '@theme/config'
import Router from '@routes/index'
import 'chartjs-adapter-luxon';

import {
    Chart as ChartJS,
    registerables
  } from 'chart.js';
  
  
  ChartJS.register(
    ...registerables
  );

  
export default function App () {

    return (
        <HelmetProvider>
            <ChakraProvider theme={theme}>
                <Font />
                <Router />
            </ChakraProvider>
        </HelmetProvider>
    )
}
