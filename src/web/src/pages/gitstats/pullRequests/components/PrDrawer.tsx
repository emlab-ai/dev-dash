import { ExternalLinkIcon } from "@chakra-ui/icons";
import { Box, Text, Button, Drawer, DrawerBody, DrawerCloseButton, DrawerContent, DrawerFooter, DrawerHeader, DrawerOverlay, FormLabel, HStack, Heading, Link, VStack } from "@chakra-ui/react";
import { useMemo } from "react";
import { Doughnut } from "react-chartjs-2";

export default function PrDrawer({ isOpen, onClose, currentItem }: { isOpen: boolean, onClose: () => void, currentItem: any }) {
    const data = useMemo(() => {
        return {
            labels: ['Additions', 'Deletions'],
            datasets: [
                {
                    data: [currentItem?.additions, currentItem?.deletions],
                    backgroundColor: ['#36A2EB', '#FF6384'],
                    hoverBackgroundColor: ['#36A2EB', '#FF6384'],
                },
            ],
        }
    }, [currentItem]);

    const totalChanges = useMemo(() => {
        return (currentItem?.additions || 0) + (currentItem?.deletions || 0);
    }, [currentItem]);

    const options = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: false,
            },
        },
    };

    return <Drawer
        size="md"
        isOpen={isOpen}
        placement='right'
        onClose={onClose}>
        <DrawerOverlay />
        <DrawerContent>
            <DrawerCloseButton />
            <DrawerHeader borderBottomWidth='1px'>
                Pull request details
            </DrawerHeader>

            <DrawerBody overflowY="scroll" >

                <Box py="4">
                    <Heading as="h2" size="sm" fontWeight="normal">Author Name</Heading>
                    <Text>{currentItem?.user}</Text>
                </Box>

                <Box py="4">
                    <FormLabel htmlFor='url'>Title</FormLabel>
                    <ExternalLinkIcon mx="2px" />
                    <Link href={currentItem?.url} target="_blank" rel="noopener noreferrer">{currentItem?.title}</Link>
                </Box>

                <Box py="4">
                    <Heading as="h2" size="sm" fontWeight="normal">First Commit Date</Heading>
                    <Text>{currentItem?.firstCommitDate}</Text>
                </Box>

                <Box py="4">
                    <Heading as="h2" size="sm" fontWeight="normal">First Commit Message</Heading>
                    <Text>{currentItem?.firstCommitMessage}</Text>
                </Box>

                <Box py="4">
                    <Heading as="h2" size="sm" fontWeight="normal">Created At</Heading>
                    <Text>{currentItem?.createdAt}</Text>
                </Box>

                <Box py="4">
                    <Heading as="h2" size="sm" fontWeight="normal">Closed At</Heading>
                    <Text>{currentItem?.closedAt}</Text>
                </Box>


                <Box py="4">
                    <FormLabel htmlFor='stats'>Size stats</FormLabel>

                    <Box>

                        <HStack py="2" h="48">
                            <VStack>
                                <Heading as="h3" size="sm" fontWeight="normal">Total Lines</Heading>
                                <Text fontWeight="bold" fontSize="2xl">{totalChanges}</Text>
                            </VStack>
                            <Doughnut data={data} options={options} />

                        </HStack>
                    </Box>

                </Box>

                <Box py="4">
                    <FormLabel htmlFor='desc'>Description</FormLabel>
                    <Box overflow="scroll" maxHeight="300px">
                        {currentItem?.bodyText}
                    </Box>
                </Box>
            </DrawerBody>

            <DrawerFooter borderTopWidth='1px'>
                <Button variant='outline' mr={3} onClick={onClose}>
                    Close
                </Button>
            </DrawerFooter>
        </DrawerContent>
    </Drawer>
}