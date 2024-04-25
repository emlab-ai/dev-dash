import { ExternalLinkIcon } from "@chakra-ui/icons";
import { Box, Text, Table, TableContainer, Tbody, Td, Th, Thead, Tr, VStack, HStack, Tag, Link, Avatar, Tooltip } from "@chakra-ui/react";
import { PullRequest } from "@src/providers/pullRequestsViewModel";
import { FaCodeBranch } from "react-icons/fa";
import { TableCellDate } from "./TableCellDate";
import { TableCellDuration } from "./TableCellDuration";
import { TableCellCodeDelta } from "./TableCellCodeDelta";

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
                            <Td pl={0}><TableCellDate date={pr.createdAt}/></Td>
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
                            <Td pl={0} textAlign="left"><TableCellCodeDelta deletions={pr.deletions} additions={pr.additions}/></Td>
                            <Td pl={0}><TableCellDuration hours={pr.totalDuration}/></Td>
                        </Tr>
                    ))}
                </Tbody>
            </Table>
        </TableContainer>
    )
}

const PrStatus = ({status, date}:any) => {
    return (
        <HStack spacing={2}>
            <Tag size="sm" variant="solid" colorScheme="purple">
                <HStack p={2} spacing={1} justify="center">
                    <FaCodeBranch />
                    <Text>{status}</Text>
                </HStack>
            </Tag>
            <TableCellDate date={date}/>
        </HStack>
    )
}

