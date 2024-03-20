import { AspectRatio, Badge, Box, Container, Grid, GridItem, HStack, Heading, Select, Tab, TabList, TabPanel, TabPanels, Tabs, Text, VStack, useToken } from "@chakra-ui/react"
import { Line } from 'react-chartjs-2';
import { useColorModeValue } from "@chakra-ui/react";
import { Suspense } from "react";
import { DashboardProvider, useDashboardContext } from "@src/providers/dashboardViewModel";


export default function DashboardPage() {
  return (
    <DashboardProvider>
    <Box bg="gray.50" minH="100vh" py="4">
    
    <HStack justify="space-between" px="4">
      <Box>
        <HStack>
          <Text>Timeframe:</Text>
          <Select w="100%" placeholder="Select timeframe">
            <option value="last-month">Last month</option>
            <option value="last-6-months">Last 6 months</option>
            <option value="last-12-months">Last 12 months</option>
          </Select>
        </HStack>
      </Box>
      <Box>
        <HStack>
          <Text>Manager:</Text>
          <Select w="100%" placeholder="Select manager" />
        </HStack>
      </Box>
    </HStack>
      <Tabs>
        <TabList>
          <Tab>Manager metrics</Tab>
          <Tab>Tab 2</Tab>
        </TabList>
        <TabPanels>
          <TabPanel>
            <Container w="100%" maxW="full">
              <VStack spacing="4">
                <TopLineSummary />
                <DiffStatsSummary />
              </VStack>
              {/* <AccountStats />
              <StatsSimpleGrid />
              <StatsBar  />
              <ProgressBarGrid />
              <StatsSimpleIconGrid /> */}
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
    </DashboardProvider>
  )
}

const number_to_percent_str = (value: number) => { return (value * 100).toFixed(2) + "%"; }



const LineChart = () => {
  const primaryColor = useToken("colors", useColorModeValue("blue.500", "blue.200"));
  const secondaryColor = useToken("colors", useColorModeValue("green.500", "green.200"));
  const tertiaryColor = useToken("colors", useColorModeValue("red.500", "red.200")) ;

  const data: any = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
    datasets: [
      {
        label: 'Line 1',
        data: [12, 19, 3, 5, 2, 3, 8, 10, 15, 7],
        fill: true,
        cubicInterpolationMode: 'monotone',
        backgroundColor: primaryColor,
        borderColor: primaryColor,
      },
      {
        label: 'Line 2',
        fill: true,
        data: [5, 8, 10, 6, 12, 15, 9, 4, 7, 11],
        borderColor: secondaryColor,
        backgroundColor: secondaryColor,
      },
      {
        label: 'Line 3',
        data: [9, 6, 11, 4, 7, 13, 8, 5, 10, 3],
        borderColor: tertiaryColor,
        backgroundColor: 'transparent',
      },
    ],
  };

  const options = {
    scales: {
      x: {
        min: -2,
        max: 800,
        title: {
          display: true,
          text: 'Date',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Value',
        },
      },
    },
  };

  return <AspectRatio ratio={16 / 9}>
    <Line data={data} options={options} />
  </AspectRatio>;
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
            <GridItem w='100%'>
              <StatsSimple key={stat.id} title={stat.label} value={stat.value} delta={stat.diffPercent} />
            </GridItem>
        )}
              
      </Grid>
    </Suspense>
  )
}

const TopLineSummary = () => {
  return (
    <>
      <StatsSimpleGrid />
    </>
  )
}

const DiffStatsSummary = () => {
  return (
    <>
      <Heading as="h1" fontWeight="normal">PRs metrics</Heading>
      <Grid templateColumns={{ base: 'repeat(1, 1fr)', md: 'repeat(2, 1fr)' }} gap={4} w="100%">
        <GridItem>
          <LineChart />
        </GridItem>
        <GridItem>
          <LineChart />
        </GridItem>
        <GridItem>
        <LineChart />
        </GridItem>
        <GridItem>
          <LineChart />
        </GridItem>
      </Grid>
    </>
  )
}


const InfoBox = ({ title, subTitle }: { title: string, subTitle?: string }) => {
  return (
    <Box bg="lightGrey" rounded="md" shadow="sm" p="4">
      <Heading as="h2" size="sm" fontWeight="normal">{title}</Heading>
      {subTitle && <Text size="sm">{subTitle} </Text>}
    </Box>
  )
}

const StatsSimple = ({ title, value, delta, subTitle }: { title: string, value: number, delta: number, subTitle?: string }) => {
  return (
    <Box bg="white" rounded="md" shadow="sm" p="4">
      <Heading as="h2" size="sm" fontWeight="normal">{title}</Heading>
      <HStack py="2">
        <Text fontWeight="bold" fontSize="2xl">{value}</Text>

        <Badge fontSize="md" colorScheme={(delta < 0 ? "red" : "green")}>{number_to_percent_str(delta)}</Badge>
      </HStack>
      {subTitle && <Text size="sm">{subTitle} </Text>}
    </Box>
  )
}
