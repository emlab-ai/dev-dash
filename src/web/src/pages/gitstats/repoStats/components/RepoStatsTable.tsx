import { Box} from "@chakra-ui/react";
import { TableCellDuration } from "@src/components/TableCellDuration";
import { VirtualizedDataTable } from "@src/components/VirtualizedDataTable";
import { useReposStatsContext } from "@src/providers/reposStatsViewModel";
import { useMemo } from "react";

export const RepoStatsTable = ({ onClickOnLine }: { onClickOnLine: (onClickOnLine: any) => void }) => {
    const { setSorting, reposStatsQuery } = useReposStatsContext();
    
    const columns = useMemo(
        () => [
            {
                header: 'Repository name',
                id: 'name',
                size: 500,                
                accessorKey: 'name',
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
            <VirtualizedDataTable columns={columns} query={reposStatsQuery} onSortingChange={setSorting} onRowClick={onClickOnLine}/>            
        </Box>
    );
};