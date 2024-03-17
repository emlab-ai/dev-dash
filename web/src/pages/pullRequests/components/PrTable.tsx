import { Tr, Td, Table, Thead, Th, Tbody, Link, VStack, Box, HStack, Text, Heading, Divider, TableContainer, useColorModeValue, Avatar } from "@chakra-ui/react";
import { usePullRequestsContext, PullRequest } from "@src/providers/pullRequestsViewModel";
import { ExternalLinkIcon } from "@chakra-ui/icons";
import { NavLink } from "react-router-dom";
import { TableCellDuration } from "@src/components/TableCellDuration";
import { TableCellCodeDelta } from "@src/components/TableCellCodeDelta";
import Pager from "@src/components/Pager";

const PrTable = ({ onClickOnLine }: { onClickOnLine: (onClickOnLine: PullRequest) => void }) => {
    const { pullRequests, nextPage, prevPage, hasNextPage, hasPrevPage } = usePullRequestsContext();
    const hoverColor = useColorModeValue("blackAlpha.100", "whiteAlpha.100");

    return (
        <Box width="100%" pl={8} pr={8}>
            <TableContainer>
                <Table variant="simple" width="100%" >
                    <Thead>
                        <Tr>
                            <Th></Th>
                            <Th w="600px">Title</Th>
                            <Th>LoC</Th>
                            <Th>Total time (hours)</Th>                            
                            <Th isNumeric>Files changed</Th>
                            <Th isNumeric>Review threads</Th>
                            <Th isNumeric>Resolved comments</Th>
                            <Th isNumeric>Comments</Th>
                        </Tr>
                    </Thead>
                    <Tbody>
                        {pullRequests.map((pr) => (                        
                            <Tr key={pr.id} onClick={() => onClickOnLine(pr)} _hover={{ bg: hoverColor, cursor: "pointer" }}>
                                <Td>                                    
                                    <Avatar size="sm" name={pr.author_name}/>
                                </Td>
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
                                                &nbsp; created by <NavLink to={`/usersstats/${pr.authorId}`}>@{pr.author}</NavLink> </Text>
                                        </Box>
                                    </VStack>
                                </Td>
                                <Td><TableCellCodeDelta additions={pr.additions} deletions={pr.deletions}/></Td>
                                <Td><TableCellDuration hours={pr.totalDuration} /></Td>                                
                                <Td isNumeric>{pr.changedFiles}</Td>
                                <Td isNumeric>{pr.reviewThreadsCount}</Td> 
                                <Td isNumeric>{pr.resolvedCommentsCount}</Td>
                                <Td isNumeric>{pr.commentsCount}</Td>
                            </Tr>
                        ))}
                    </Tbody>
                </Table>
            </TableContainer>
            <Divider />
            <Pager nextPage={nextPage} prevPage={prevPage} hasNext={hasNextPage} hasPrev={hasPrevPage}/>
        </Box>


    );
};

export default PrTable;