import { Link, VStack, Box,  Text, Heading, Avatar } from "@chakra-ui/react";
import { usePullRequestsContext, PullRequest } from "@src/providers/pullRequestsViewModel";
import { ExternalLinkIcon } from "@chakra-ui/icons";
import { NavLink } from "react-router-dom";
import { TableCellDuration } from "@src/components/TableCellDuration";
import { TableCellCodeDelta } from "@src/components/TableCellCodeDelta";
import { useMemo } from "react";
import { VirtualizedDataTable } from "@src/components/VirtualizedDataTable";

const PrTable = ({ onClickOnLine }: { onClickOnLine: (onClickOnLine: PullRequest) => void }) => {
    const { pullRequestQuery, setSorting } = usePullRequestsContext();
    const columns = useMemo(
        () => [
            {
                header: '',
                id: 'author_name',
                size: 40,                
                accessorKey: 'author_name',
                cell: ({ row }: any) => (
                    <Avatar size="sm" name={row.original.author_name} />
                ),
                sortable: false
            },
            {
                header: 'Title',
                id: 'title',
                size: 800,
                accessorKey: 'title',
                cell: ({ row }: any) => {
                    const pr = row.original;
                    return <VStack width="100%" align="left" mt={4} mb={4}>
                        <Heading as="h2" size="sm" maxH="40px" overflow="hidden" textOverflow="ellipsis" whiteSpace="nowrap">{pr.title}</Heading>
                        <Box>
                            <Text size="sm">
                                <Link href={pr.url} target="_blank" rel="noopener noreferrer" title={pr.title}>
                                    <ExternalLinkIcon mx="2px" />
                                    #{pr.number}
                                </Link>&nbsp;
                                {pr.state} {new Date(pr.closedAt).toLocaleDateString()}
                                &nbsp; created by <NavLink to={`/gitstats/users/${pr.authorId}`}>@{pr.author}</NavLink> </Text>
                        </Box>
                    </VStack>
                },
                sortable: false
            },
            {
                header: 'LoC',
                id: 'changes',
                size: 120,
                accessorKey: 'changes',
                cell: ({ cell: { row } }: any) => (
                    <TableCellCodeDelta additions={row.original.additions} deletions={row.original.deletions} />
                ),
            },
            {
                header: 'Cycle time',
                id: 'totalDuration',
                size: 120,
                accessorKey: 'totalDuration',
                cell: ({ row }: any) => (
                    <TableCellDuration hours={row.original.totalDuration} />
                ),
            },
            {
                header: 'Files changed',
                id: 'changedFiles',
                accessorKey: 'changedFiles'
            },
            {
                header: 'Review threads',
                id: 'reviewThreadsCount',
                accessorKey: 'reviewThreadsCount'
            },
            {
                header: 'Comments',
                id: 'commentsCount',
                accessorKey: 'commentsCount'
            }
        ],
        []
    );

    return (
        <Box width="100%">
            <VirtualizedDataTable columns={columns} query={pullRequestQuery} onSortingChange={setSorting} onRowClick={onClickOnLine}/>            
        </Box>
    );
};

export default PrTable;