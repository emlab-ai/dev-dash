import { Box, Container, Text, useDisclosure, Avatar, Flex } from "@chakra-ui/react";
import ScopeFilter from "@src/components/ScopeFilter";
import { useUsersStatsContext } from "@src/providers/usersStatsViewModel";
import { useCallback, useEffect, useMemo, useState } from "react";
import { UserDetailsDrawer } from "./components/UserDetailsDrawer";
import { useParams, useNavigate } from "react-router-dom";
import { TableCellDuration } from "@src/components/TableCellDuration";
import { VirtualizedDataTable } from "@src/components/VirtualizedDataTable";

const UserStsatsTable = ({ onClickOnLine }: { onClickOnLine: (onClickOnLine: any) => void }) => {
    const { setSorting, usersStatsQuery } = useUsersStatsContext();
    
    const columns = useMemo(
        () => [
            {
                header: '',
                id: 'user_name',
                size: 40,                
                accessorKey: 'user_name',
                cell: ({ row }: any) => (
                    <Avatar size="sm" name={row.original?.user_name} />
                ),
            },
            {
                header: 'Name',
                id: 'name',
                size: 500,
                accessorKey: 'github_login',
                cell: ({ row }: any) => {
                    var stat = row.original;
                    return <Text>{stat?.user_name || stat?.github_login}</Text>
                },
            },
            {
                header: '# of PRs',
                id: 'count',
                accessorKey: 'count'
            },
            {
                header: 'Avg: Duration',
                id: 'avg_duration',
                size: 120,
                accessorKey: 'avg_duration',
                cell: ({ cell: { row } }: any) => (
                    <TableCellDuration hours={row.original?.avg_duration}/>
                ),
            },
            {
                header: 'Max: Duration',
                id: 'max_duration',
                size: 120,
                accessorKey: 'max_duration',
                cell: ({ cell: { row } }: any) => (
                    <TableCellDuration hours={row.original?.max_duration}/>
                ),
            },
            {
                header: 'Team',
                id: 'user_team',
                accessorKey: 'user_team'
            },            
            {
                header: 'Avg: LoC',
                id: 'avg_loc',
                accessorKey: 'avg_loc'
            },
            {
                header: 'Max: LoC',
                id: 'max_loc',
                accessorKey: 'max_loc'
            },
            {
                header: 'Sum: LoC',
                id: 'sum_loc',
                accessorKey: 'sum_loc'
            }
        ],
        []
    );

    return (
        <Box width="100%">
            <VirtualizedDataTable columns={columns} query={usersStatsQuery} onSortingChange={setSorting} onRowClick={onClickOnLine}/>            
        </Box>
    );
};


export default function UsersStatsPage() {
    const navigate = useNavigate();
    const { isOpen, onOpen, onClose } = useDisclosure({
        onClose: () => navigate(`/usersstats`)
    })
    const [currentItem, setCurrentItem] = useState<number | undefined>();

    const onClickOnLine = useCallback((row:any) => {
        navigate(`/usersstats/${row.id}`);
    }, [onOpen, navigate]);

    const { id } = useParams<{ id: string }>();

    useEffect(() => {
        if(id) {
            setCurrentItem(parseInt(id, 10));
            onOpen();
        } else if (isOpen){
            onClose();
        }
    }, [id]);

    const { managerFilter, setManagerFilter, timeFilter, setTimeFilter } = useUsersStatsContext();
    return (
        <>
            <Flex flexDir="column" w="100%" h="100%" pl={4} pr={4}>
                <ScopeFilter managerFilter={managerFilter} timeFilter={timeFilter} setTimeFilter={setTimeFilter} setManagerFilter={setManagerFilter }  />

                <Container w="100%" maxW="full" flex={1} position="relative">
                    <UserStsatsTable onClickOnLine={onClickOnLine} />
                </Container>
            </Flex>
            {<UserDetailsDrawer isOpen={isOpen} onClose={onClose} userId={currentItem} />}
        </>
    )
}