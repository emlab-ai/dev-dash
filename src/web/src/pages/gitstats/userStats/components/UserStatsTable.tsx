import { Avatar, Box, Text} from "@chakra-ui/react";
import { TableCellDuration } from "@src/components/TableCellDuration";
import { VirtualizedDataTable } from "@src/components/VirtualizedDataTable";
import { useUsersStatsContext } from "@src/providers/usersStatsViewModel";
import { useMemo } from "react";

export const UserStatsTable = ({ onClickOnLine }: { onClickOnLine: (onClickOnLine: any) => void }) => {
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