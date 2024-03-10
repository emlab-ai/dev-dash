import { Tr, Td, Table, Thead, Th, Tbody, Link, VStack, Box, HStack, Text, Heading, Divider, TableContainer, useColorModeValue } from "@chakra-ui/react";
import { usePullRequestsContext, PullRequest } from "@src/providers/pullRequestsViewModel";
import { ExternalLinkIcon } from "@chakra-ui/icons";
import { NavLink } from "react-router-dom";

const PrTable = ({ onClickOnLine }: { onClickOnLine: (onClickOnLine: PullRequest) => void }) => {
    const { pullRequests, nextPage, prevPage, hasNextPage, hasPrevPage } = usePullRequestsContext();

    return (
        <Box width="100%" pl={8} pr={8}>
            <TableContainer>
                <Table variant="simple" width="100%" >
                    <Thead>
                        <Tr>
                            <Th w="600px">Title</Th>
                            <Th>LoC</Th>
                            <Th>Total time (hours)</Th>                            
                            <Th>Files changed</Th>
                            <Th>Review threads</Th>
                            <Th>Resolved comments</Th>
                            <Th>Comments</Th>
                        </Tr>
                    </Thead>
                    <Tbody>
                        {pullRequests.map((pr) => (
                            <Tr key={pr.id} onClick={() => onClickOnLine(pr)} _hover={{ bg: useColorModeValue("blackAlpha.100", "whiteAlpha.100"), cursor: "pointer" }}>
                                <Td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                    <VStack width="100%" align="left">
                                        <Heading as="h2" size="sm">{pr.title}</Heading>
                                        <Box>
                                            <Text size="sm">
                                                <Link href={pr.repositoryUrl+"/pull/"+pr.number} target="_blank" rel="noopener noreferrer" title={pr.title}>
                                                    <ExternalLinkIcon mx="2px" />
                                                    #{pr.number}
                                                </Link>&nbsp;
                                                closed {new Date(pr.closedAt).toLocaleDateString()}
                                                &nbsp; created by <NavLink to={`/usersstats/${pr.authorId}`}><Link>@{pr.author}</Link></NavLink> </Text>
                                        </Box>
                                    </VStack>
                                </Td>
                                <Td>{(pr.additions || 0) + (pr.deletions || 0)}</Td>
                                <Td>{pr.totalDuration.toFixed(2)}</Td>                                
                                <Td>{pr.changedFiles}</Td>
                                <Td>{pr.reviewThreadsCount}</Td> 
                                <Td>{pr.resolvedCommentsCount}</Td>
                                <Td>{pr.commentsCount}</Td>
                            </Tr>
                        ))}
                    </Tbody>
                </Table>
            </TableContainer>
            <Divider />
            <HStack justifyContent="center" pt={4} pb={8}>
                <Link pointerEvents={hasPrevPage?"all":"none"} onClick={prevPage}>&lt;&nbsp;Previous</Link>
                <Link pointerEvents={hasNextPage?"all":"none"} onClick={nextPage} pl={2}>Next&nbsp;&gt;</Link>
            </HStack>
        </Box>


    );
};

export default PrTable;