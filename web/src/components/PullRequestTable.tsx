import { ExternalLinkIcon } from "@chakra-ui/icons";
import { useColorModeValue, Box, Text, Table, TableContainer, Tbody, Td, Th, Thead, Tr, VStack, HStack, Tag, Link, Avatar, Tooltip } from "@chakra-ui/react";
import { PullRequest } from "@src/providers/pullRequestsViewModel";
import { FaCodeBranch } from "react-icons/fa";

export default function PullRequestTable({data}:any) {
    return (
        <TableContainer>
            <Table size="sm" width="100%">
                <Thead>
                    <Tr>
                        <Th pl={0}>Autor</Th>
                        <Th pl={0}>Created</Th>
                        <Th pl={0}><Box flex={1}>Title</Box></Th>
                        <Th pl={0}>Status</Th>
                        <Th pl={0}>+/-</Th>
                        <Th pl={0}>Cycle Time</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {data.map((pr:PullRequest) => (
                        <Tr key={pr.id} borderBottom="1px solid" borderColor="blue.500">
                            <Td pl={0}>
                                <Tooltip label={pr.author} aria-label="Author" placement="top">
                                    <Avatar name={pr.author_name} size="sm" />
                                </Tooltip>
                            </Td>
                            <Td pl={0}><PrDate date={pr.createdAt}/></Td>
                            <Td pl={0}>
                                <VStack flex={1} spacing={1} align="flex-start">
                                    <Link href={pr.repositoryUrl+"/pull/"+pr.number} target="_blank" rel="noopener noreferrer" title={pr.title}>
                                        <HStack><ExternalLinkIcon mx="1px" />
                                            <Text isTruncated maxW="300px">{pr.title}</Text>
                                        </HStack>
                                    </Link>
                                    <Text fontSize="xs">{pr.repositoryName}</Text>
                                </VStack>
                            </Td>                            
                            <Td pl={0}><PrStatus status={"Merged"} date={pr.closedAt}/></Td>
                            <Td pl={0} textAlign="left"><PrDelta deletions={pr.deletions} additions={pr.additions}/></Td>
                            <Td pl={0}><DurationDisplay hours={pr.totalDuration}/></Td>
                        </Tr>
                    ))}
                </Tbody>
            </Table>
        </TableContainer>
    )
}

const PrDelta = ({deletions, additions}: {deletions: number, additions: number}) => {
    const changes = additions + deletions;
    const bred = changes > 100;
    return (
        <Box pl={1} pr={1} bg={bred?useColorModeValue('red.100', 'red.100'):undefined} color={bred?useColorModeValue('black', 'black'):undefined}>
            <VStack p={1} spacing={0} alignItems="flex-start">
                <Text fontSize="xs"><Text as="span" fontWeight="bold">{changes}</Text>&nbsp;edits</Text>
                <HStack spacing={1}>
                    <Text color={useColorModeValue('green.400', bred?'green.800':'green.400')} fontSize="2xs" fontWeight="bold">+{additions}</Text>
                    <Text color={useColorModeValue('red.800', bred?'red.800':'red.400')} fontSize="2xs" fontWeight="bold">-{deletions}</Text>
                </HStack>
            </VStack>
        </Box>
    )
}

const PrStatus = ({status, date}:any) => {
    return (
        <HStack spacing={1}>
            <Box bg="#663399" color="white" borderRadius={16} width="120px">
                <HStack p={2} spacing={1} justify="center">
                    <FaCodeBranch />
                    <Text>{status}</Text>
                </HStack>
            </Box>
            <PrDate date={date}/>
        </HStack>
    )
}

const PrDate = ({date}:any) => {
    return (
        <VStack align="flex-start" spacing={0}>
            <Text fontSize="xs">{new Date(date).toLocaleDateString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '/')}</Text>
            <Text fontSize="2xs">{new Date(date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</Text>
        </VStack>
    )
}

const DurationDisplay = ({hours}: {hours:number}) => { 
    if (hours >= 24) { 
        const days = Math.floor(hours / 24); 
        const remainingHours = hours % 24; 
        return <Text><Text as="span" fontWeight="semibold">{days}</Text> d <Text as="span" fontWeight="semibold">{Math.floor(remainingHours)}</Text> h</Text>; 
    } else { 
        const minutes = hours * 60; 
        const remainingMinutes = minutes % 60; 
        return <Text><Text as="span" fontWeight="semibold">{Math.floor(minutes / 60)}</Text> h <Text as="span" fontWeight="semibold">{Math.floor(remainingMinutes)}</Text> m</Text>; 
    } 
};