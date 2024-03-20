import { Box, Drawer, DrawerBody, Text, DrawerCloseButton, DrawerContent, DrawerHeader, DrawerOverlay, HStack, Avatar, TabPanels, Tabs, Tab, TabList, TabPanel } from "@chakra-ui/react";
import DateFilterToggle from "@src/components/DateFilterToggle";
import Pager from "@src/components/Pager";
import { PullRequestReviewsTable } from "@src/components/PullRequestReviewsTable";
import PullRequestTable from "@src/components/PullRequestTable";
import { UserDetailsProvider, useUserDetailsContext } from "@src/providers/userDetailsViewModel";
import { Bar } from 'react-chartjs-2';

interface UserDetailsDrawerProps {
    isOpen: boolean;
    userId?: number;
    onClose: () => void;
}

export function UserDetailsDrawer({ isOpen, onClose, userId }: UserDetailsDrawerProps) {
    return (
        <UserDetailsProvider id={userId}>
            <UserDetailsDrawerContent isOpen={isOpen} onClose={onClose} userId={userId} />
        </UserDetailsProvider>
    );
}

function UserDetailsDrawerContent({ isOpen, onClose, userId }: UserDetailsDrawerProps) {
    var { user } = useUserDetailsContext();

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
                    <Avatar size="md" name={user?.name} /> <Text>{user?.name}</Text>
                </HStack>
            </DrawerHeader>
            <DrawerBody overflowY="scroll">
                <UserDetailsContent userId={userId} />
            </DrawerBody>            
        </DrawerContent>
    </Drawer>
}

function UserDetailsContent({ userId }: { userId?: number }) {
    var context = useUserDetailsContext();
    const chartData = {
        labels: context.userPrsChart?.labels,
        datasets: [
            {
                label: 'Pull Requests',
                data: context.userPrsChart?.data,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
            },
            {
                label: 'Reviews',
                data: context.userReviewsChart?.data,
                backgroundColor: '#ffc00033',
                borderColor: '#ffc000',
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
                    <Tab>Code Reviews</Tab>
                </TabList>
                <TabPanels>
                    <TabPanel>
                        <PullRequestTable data={context.pullRequests}></PullRequestTable>
                        <Pager nextPage={context.nextPullReqestPage} prevPage={context.prevPullReqestPage} hasNext={context.hasNextPullReqestPage} hasPrev={context.hasPrevPullReqestPage} />
                    </TabPanel>
                    <TabPanel>
                        <PullRequestReviewsTable userId={userId ?? 0} startDate={context.startDate} endDate={context.endDate} />
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Box>
    );
}   