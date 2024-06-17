import { ExternalLinkIcon } from "@chakra-ui/icons";
import { Box, Drawer, DrawerBody, DrawerCloseButton, DrawerContent, DrawerHeader, DrawerOverlay, HStack, TabPanels, Tabs, Tab, TabList, TabPanel, Link } from "@chakra-ui/react";
import DateFilterToggle from "@src/components/DateFilterToggle";
import Pager from "@src/components/Pager";
import PullRequestTable from "@src/components/PullRequestTable";
import { RepoDetailsProvider, useRepoDetailsContext } from "@src/providers/repoDetailsViewModel";
import { Bar } from 'react-chartjs-2';

interface RepoDetailsDrawerProps {
    isOpen: boolean;
    repoId?: number;
    onClose: () => void;
}

export function RepoStatsDetailsDrawer({ isOpen, onClose, repoId }: RepoDetailsDrawerProps) {
    return (
        <RepoDetailsProvider id={repoId}>
            <RepoStatsDetailsDrawerContent isOpen={isOpen} onClose={onClose} repoId={repoId} />
        </RepoDetailsProvider>
    );
}

function RepoStatsDetailsDrawerContent({ isOpen, onClose }: RepoDetailsDrawerProps) {
    var { repo } = useRepoDetailsContext();

    return <Drawer
        isOpen={isOpen}
        placement="right"
        onClose={onClose}
        size="xl"
    >
        <DrawerOverlay />
        <DrawerContent>
            <DrawerCloseButton />
            <DrawerHeader>
                <HStack alignItems="center">
                    <Link href={"https://github.com/"+repo?.name} target="_blank"><ExternalLinkIcon boxSize={4} color="gray.500" />&nbsp;{repo?.name}</Link>
                </HStack>
            </DrawerHeader>
            <DrawerBody overflowY="scroll">
                <RepoStatsDetailsContent />
            </DrawerBody>            
        </DrawerContent>
    </Drawer>
}

function RepoStatsDetailsContent() {
    var context = useRepoDetailsContext();
    const chartData = {
        labels: context.repoPrsChart?.labels,
        datasets: [
            {
                label: 'Pull Requests',
                data: context.repoPrsChart?.data,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
            }
        ],
    };

    // Define the options for the bar chart
    const chartOptions = {
        scales: {
            x: {
                time: {
                    unit: 'day',
                    tooltipFormat: 'll',
                    displayFormats: {
                        day: 'MMM d'
                    }
                },
                ticks: {
                    maxRotation: 0,
                    autoSkip: true,
                },
                stacked: true
            },
            y: {
                beginAtZero: true,
                stacked: true
            },
        },
    };

    return (
        <Box>
            <HStack>
                <DateFilterToggle value={context.timeFilter} onChange={context.setTimeFilter} size="xs" />
            </HStack>
            <Bar data={chartData} options={chartOptions} height="100px" />
            <Tabs>
                <TabList>
                    <Tab>Pull Requests</Tab>
                </TabList>
                <TabPanels>
                    <TabPanel>
                        <PullRequestTable data={context.pullRequests}></PullRequestTable>
                        <Pager nextPage={context.nextPullReqestPage} prevPage={context.prevPullReqestPage} hasNext={context.hasNextPullReqestPage} hasPrev={context.hasPrevPullReqestPage} />
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Box>
    );
}   