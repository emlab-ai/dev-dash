import { ExternalLinkIcon } from "@chakra-ui/icons";
import { useColorModeValue, Box, Text, Table, TableContainer, Tbody, Td, Th, Thead, Tr, VStack, HStack, Tag, Link } from "@chakra-ui/react";
import { FaCodeBranch } from "react-icons/fa";

export default function PullRequestTable({data}:any) {
    return (
        <TableContainer>
            <Table size="sm" width="100%">
                <Thead>
                    <Tr>
                        <Th pl={0}>Created</Th>
                        <Th pl={0}><Box flex={1}>Title</Box></Th>
                        <Th pl={0}>Autor</Th>
                        <Th pl={0}>Status</Th>
                        <Th pl={0}>+/-</Th>
                        <Th pl={0}>Cycle Time</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {data.map((pr:any) => (
                        <Tr key={pr.id} borderBottom="1px solid" borderColor="blue.500">
                            <Td pl={0}>{pr.createdAt}</Td>
                            <Td pl={0}><Box flex={1}>
                            <Link href={pr.repositoryUrl+"/pull/"+pr.number} target="_blank" rel="noopener noreferrer" title={pr.title}>
                                <HStack><ExternalLinkIcon mx="1px" />
                                    <Text isTruncated maxW="300px">{pr.title}</Text>
                                </HStack>
                            </Link>
                                
                            </Box></Td>
                            <Td pl={0}>{pr.gitAlias}</Td>
                            <Td pl={0}><PrStatus status={pr.status} date={pr.closedAt}/></Td>
                            <Td pl={0} textAlign="left"><PrDelta deletions={pr.deletions} additions={pr.additions}/></Td>
                            <Td pl={0}>{pr.duration}</Td>
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
        <Box bg={bred?useColorModeValue('red.100', 'red.100'):undefined} color={bred?useColorModeValue('black', 'black'):undefined}>
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
        <Box bg="#663399" color="white" borderRadius={16} width="120px">
            <HStack p={2} spacing={1} justify="center">
                <FaCodeBranch />
                <Text>Merged</Text>
            </HStack>
        </Box>

    )
}