import { Box, Drawer, DrawerBody, Text, DrawerCloseButton, DrawerContent, DrawerHeader, DrawerOverlay, HStack, VStack, Avatar, Accordion, AccordionButton, AccordionIcon, AccordionItem, AccordionPanel } from "@chakra-ui/react";
import Pager from "@src/components/Pager";
import { PullRequestReviewsTable } from "@src/components/PullRequestReviewsTable";
import PullRequestTable from "@src/components/PullRequestTable";
import { UserDetailsProvider, useUserDetailsContext } from "@src/providers/userDetailsViewModel";
import { Bar } from 'react-chartjs-2';

interface UserDetailsDrawerProps {
    isOpen: boolean;
    userId: number;
    onClose: () => void;
}

export function UserDetailsDrawer({isOpen, onClose, userId}: UserDetailsDrawerProps){
    return (
        <UserDetailsProvider id={userId}>
            <UserDetailsDrawerContent isOpen={isOpen} onClose={onClose} userId={userId} />
        </UserDetailsProvider>
    );
}

function UserDetailsDrawerContent({isOpen, onClose, userId}: UserDetailsDrawerProps) {
    var {user} = useUserDetailsContext();

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
                    <Avatar size="md" name={user?.name}/> <Text>{user?.name}</Text>
                </HStack>
            </DrawerHeader>
            <DrawerBody>
                <UserDetailsContent userId={userId}/>
            </DrawerBody>
        </DrawerContent>
    </Drawer>
}

function UserDetailsContent({userId}: {userId: number}) {
    var {
        userPrsChart, 
        pullRequests,
        nextPullReqestPage,
        prevPullReqestPage,
        hasNextPullReqestPage,
        hasPrevPullReqestPage,
        startDate,
        endDate
    } = useUserDetailsContext();
    const chartData = {
        labels: userPrsChart?.labels,
        datasets: [
            {
                label: 'PRs',
                data: userPrsChart?.data,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
            },
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
            },
            y: {
                beginAtZero: true,
            },
        },
    };

    return (
        <Box>
            <Bar data={chartData} options={chartOptions} height="100px" />
            <Accordion allowToggle defaultIndex={0}>
                <AccordionItem>
                    <h2>
                        <AccordionButton>
                            <Box flex="1" textAlign="left">
                                Pull Requests
                            </Box>
                            <AccordionIcon />
                        </AccordionButton>
                    </h2>
                    <AccordionPanel pb={4}>
                        {/* Content for PRs tab */}
                        <PullRequestTable data={pullRequests}></PullRequestTable>
                        <Pager nextPage={nextPullReqestPage} prevPage={prevPullReqestPage} hasNext={hasNextPullReqestPage} hasPrev={hasPrevPullReqestPage} />
                    </AccordionPanel>
                </AccordionItem>
                <AccordionItem>
                    <h2>
                        <AccordionButton>
                            <Box flex="1" textAlign="left">
                                Code Reviews
                            </Box>
                            <AccordionIcon />
                        </AccordionButton>
                    </h2>
                    <AccordionPanel pb={4}>
                        <PullRequestReviewsTable userId={userId} startDate={startDate} endDate={endDate}/>
                    </AccordionPanel>
                </AccordionItem>
            </Accordion>
        </Box>
    );
}   