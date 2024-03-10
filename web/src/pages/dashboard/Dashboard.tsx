import { AspectRatio, Badge, Box, Container, Grid, GridItem, HStack, Heading, Icon, Progress, Select, Stat, StatArrow, StatHelpText, StatLabel, StatNumber, Tab, TabList, TabPanel, TabPanels, Tabs, Text, VStack, useToken } from "@chakra-ui/react"
import { Bar, Line } from 'react-chartjs-2';
import { useColorModeValue } from "@chakra-ui/react";
import { Suspense } from "react";
import { LineChartData, useDashboardContext } from "@src/providers/dashboardViewModel";
import ScopeFilter from "@src/components/ScopeFilter";

export default function Dashboard() {
  var { managerFilter, setManagerFilter, timeFilter, setTimeFilter } = useDashboardContext();
  return (
    <Box bg={useColorModeValue('gray.50', 'gray.900')} minH="100vh" py="4">

      <ScopeFilter timeFilter={timeFilter} setTimeFilter={setTimeFilter} managerFilter={managerFilter} setManagerFilter={setManagerFilter} />
      
      <Tabs>
        <TabList>
          <Tab>Manager metrics</Tab>
          <Tab>Tribe level metrics</Tab>
        </TabList>
        <TabPanels>
          <TabPanel>
            <Container w="100%" maxW="full">
              <VStack spacing="4">
                <StatsSimpleGrid />
                <DiffStatsSummary />
              </VStack>
            </Container>
          </TabPanel>
          <TabPanel>
            <Container w="100%" maxW="full">
              test
            </Container>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  )
}

const number_to_percent_str = (value: number) => { return (value * 100).toFixed(2) + "%"; }



const LineChart = ({ data }: { data: LineChartData }) => {
  const colors: string[] = [useToken("colors", useColorModeValue("blue.500", "blue.200")),
  useToken("colors", useColorModeValue("green.500", "green.200")),
  useToken("colors", useColorModeValue("red.500", "red.200"))];

  const gridColor = useToken("colors", useColorModeValue("gray.300", "gray.500"))

  if (data) {
    for (let i = 0; i < Math.min(3, data.datasets.length); i++) {
      data.datasets[i].backgroundColor = colors[i];
      data.datasets[i].borderColor = colors[i];       
    }

    let datapoints = data.labels.map((datapoint: string) => new Date(datapoint)); // Convert each datapoint from string to date
    data.labels = datapoints;
  }

  const sampleData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
    datasets: [
      {
        label: 'Line 1',
        data: [12, 19, 3, 5, 2, 3, 8, 10, 15, 7],
        fill: true,
        cubicInterpolationMode: 'monotone',
        backgroundColor: colors[0],
        borderColor: colors[0],
      }
    ],
  };

  const options = {
    scales: {
      x: {
         grid: { color: gridColor },
        type: 'time',
        time: {
            unit: 'day',
            tooltipFormat: 'll',
            displayFormats: {
                day: 'MMM d'
            }
        },
        ticks: {
          // Customize the tick labels...
          maxRotation: 0, // Prevents the labels from being inclined
          autoSkip: true, // Prevent automatic skipping of labels          
      },
        title: {
          display: true,
          text: 'Date'
        },
      },
      y: {
        grid: { color: gridColor },
        title: {
          display: true,          
          text: 'Value',
        },
      }      
    },
    
  };

  return <Box>
    <Heading as="h2" size="md" pb="4">{data?.title}</Heading>
    <AspectRatio ratio={16 / 9}>
      <Line data={data ?? sampleData} options={options} />
    </AspectRatio>
  </Box>;
};

const StatsSimpleGrid = () => {
  var viewModel = useDashboardContext();
  const stats = viewModel.stats;
  return (
    <Suspense fallback={<Text>Loading...</Text>}>
      <Grid templateColumns={{ base: 'repeat(1, 1fr)', md: 'repeat(2, 1fr)', lg: 'repeat(6, 1fr)' }} gap={4}>
        <GridItem w='100%'>
          <InfoBox title="Last 4 weeks" subTitle="average" />
        </GridItem>
        {
          stats.cues.map((stat) =>
            <GridItem w='100%' key={stat.id}>
              <StatsSimple title={stat.label} value={stat.value} delta={stat.diffPercent} />
            </GridItem>
          )}

      </Grid>
    </Suspense>
  )
}

const DiffStatsSummary = () => {
  const { stats } = useDashboardContext();
  return (
    <>
      <Heading as="h1" fontWeight="normal">PRs metrics</Heading>
      <Grid templateColumns={{ base: 'repeat(1, 1fr)', md: 'repeat(2, 1fr)' }} gap={4} w="100%">
        {stats.lineCharts?.map((data, index) => <GridItem key={index}><LineChart data={data} /></GridItem>)}
      </Grid>
    </>
  )
}


const InfoBox = ({ title, subTitle }: { title: string, subTitle?: string }) => {
  return (
    <Box bg={useColorModeValue('lightGrey', 'teal.600')} rounded="md" shadow="sm" p="4" h="100%" display="flex" flexDirection="column" justifyContent="center">
      <Heading as="h2" size="sm" fontWeight="normal">{title}</Heading>
      {subTitle && <Text size="sm">{subTitle} </Text>}
    </Box>
  )
}

const StatsSimple = ({ title, value, delta }: { title: string, value: number, delta: number, subTitle?: string }) => {
  return (
    <Box bg={useColorModeValue('white', 'gray.700')} rounded="md" shadow="sm" p="4">

      <Stat>
        <StatLabel>{title}</StatLabel>
        <StatNumber>{value}</StatNumber>
        <StatHelpText>
          <StatArrow type={(delta < 0 ? 'decrease' : 'increase')} />
          {number_to_percent_str(delta)}
        </StatHelpText>
      </Stat>
    </Box>
  )
}
