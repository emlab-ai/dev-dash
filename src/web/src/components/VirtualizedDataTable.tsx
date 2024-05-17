import { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import { useReactTable, flexRender, getCoreRowModel, ColumnDef, SortingState, getSortedRowModel, Row } from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import { Table, Thead, Tbody, Tr, Th, Td, Icon, Box, VStack, useColorModeValue } from "@chakra-ui/react";
import { TriangleDownIcon, TriangleUpIcon } from "@chakra-ui/icons";
import { useInfiniteQuery } from '@tanstack/react-query';
import { PagedResult } from '@src/model';

export type VirtualizedDataTableProps<Data extends object> = {
  columns: ColumnDef<Data, any>[];
  query: ReturnType<typeof useInfiniteQuery<PagedResult<Data>>>;
  onSortingChange?: (sorting: SortingState) => void;
  onRowClick?: (item: Data) => void;
};

export function VirtualizedDataTable<Data extends object>({
  columns,
  query,
  onSortingChange,
  onRowClick
}: VirtualizedDataTableProps<Data>) {
  const tableContainerRef = useRef<HTMLDivElement>(null);
  const tableHeaderRef = useRef<HTMLDivElement>(null);
  const [sorting, setSorting] = useState<SortingState>([]);

  const { data: queryData, fetchNextPage, isFetching, hasNextPage } = query;

  const flatData = useMemo(() => queryData?.pages?.flatMap(page => page.data) ?? [], [queryData, queryData?.pages]);

  const table = useReactTable({
    data: flatData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: {
      sorting,
    },
    onSortingChange: (s: any) => {
      setSorting(s);
      onSortingChange && onSortingChange(s);
      return s;
    }
  });

  const { rows } = table.getRowModel();

  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    estimateSize: () => 33,
    getScrollElement: () => tableContainerRef.current,
    overscan: 5,
  });

  const fetchMoreOnBottomReached = useCallback(
    (containerRefElement?: HTMLDivElement | null) => {
      if (containerRefElement && tableHeaderRef && tableHeaderRef.current) {
          const { scrollLeft } = containerRefElement;
          tableHeaderRef.current.scrollLeft = scrollLeft;
      }

      if (containerRefElement) {
        const { scrollHeight, scrollTop, clientHeight } = containerRefElement;
        if (scrollHeight - scrollTop - clientHeight < 500 && !isFetching && hasNextPage) {
          fetchNextPage();
          console.log('fetching more');
        }
      }
    },
    [fetchNextPage, isFetching, hasNextPage, tableHeaderRef]
  );

  useEffect(() => {
    fetchMoreOnBottomReached(tableContainerRef.current);
  }, [fetchMoreOnBottomReached, tableContainerRef.current]);

  const backgroundColor = useColorModeValue('gray.50', 'gray.900')

  return (
    <Box     
      style={{
        overflow: 'hidden',
        position: 'absolute',
        top: "0", bottom: '0', left: '0', right: '0',
      }}>
        <div ref={tableHeaderRef}
        style={{
          overflow: 'hidden',
        }}>
          <Table style={{ display: 'grid' }}>
            <Thead position="relative" background={backgroundColor} zIndex={1}>
              {table.getHeaderGroups().map(headerGroup => (
                <Tr key={headerGroup.id} style={{
                  display: 'flex',
                  width: '100%',
                }}
                  pb={2}
                >
                  {headerGroup.headers.map(header => (
                    <Th
                      key={header.id}
                      onClick={header.column.getToggleSortingHandler()}
                      pr={1}
                      pl={1}
                      style={{
                        display: 'flex',
                        width: header.getSize(),
                      }}
                      p={0}
                    >
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {{
                        asc: <Icon as={TriangleUpIcon} w={10} />,// ' 🔼',
                        desc: <Icon as={TriangleDownIcon} w={10} />//' 🔽',
                      }[header.column.getIsSorted() as string] ?? null}
                    </Th>
                  ))}
                </Tr>
              ))}
            </Thead>
          </Table>
      </div>
      <div
        className="container" 
        onScroll={e => fetchMoreOnBottomReached(e.target as HTMLDivElement)}
        ref={tableContainerRef}
        style={{
          overflow: 'auto',
          position: 'absolute',
          maxHeight: '100%',
          minHeight: '100%',
          top: "36", bottom: '0', left: '0', right: '0',
        }}
      >
        <VStack>
          <Table style={{ display: 'grid' }}>
            <Thead position="relative">
              {table.getHeaderGroups().map(headerGroup => (
                <Tr key={headerGroup.id} style={{
                  display: 'flex',
                  width: '100%',
                }}
                  pb={2}
                >
                  {headerGroup.headers.map(header => (
                    <Th
                      key={header.id}
                      onClick={header.column.getToggleSortingHandler()}
                      pr={1}
                      pl={1}
                      style={{
                        display: 'flex',
                        width: header.getSize(),
                      }}
                      p={0}
                    >
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {{
                        asc: <Icon as={TriangleUpIcon} w={10} />,// ' 🔼',
                        desc: <Icon as={TriangleDownIcon} w={10} />//' 🔽',
                      }[header.column.getIsSorted() as string] ?? null}
                    </Th>
                  ))}
                </Tr>
              ))}
            </Thead>
            <Tbody
              style={{
                display: 'grid',
                height: `${rowVirtualizer.getTotalSize()}px`,
                position: 'relative',
              }}
            >
              {rowVirtualizer.getVirtualItems().map(virtualRow => {
                const row = rows[virtualRow.index] as Row<Data>;
                return (
                  <Tr
                    data-index={virtualRow.index}
                    ref={node => rowVirtualizer.measureElement(node)}
                    key={row.id}
                    style={{
                      display: 'flex',
                      position: 'absolute',
                      transform: `translateY(${virtualRow.start}px)`,
                      width: '100%',
                      height: '66px',
                    }}
                    onClick={() => { onRowClick && onRowClick(row.original) }}
                  >
                    {row.getVisibleCells().map(cell => (
                      <Td
                        key={cell.id}
                        p={0}
                        pr={1}
                        pl={1}
                        style={{
                          display: 'flex',
                          width: cell.column.getSize(),
                          alignItems: 'center'
                        }}
                      >
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </Td>
                    ))}
                  </Tr>
                );
              })}
            </Tbody>
          </Table>
          {isFetching && <Box>Fetching More...</Box>}
        </VStack>
      </div>
    </Box>
  );
}