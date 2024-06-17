import { useCallback, useEffect, useState, createContext, useContext } from 'react';
import { useOrgProviderContext } from './orgProvider';
import { useTimeFilterDates } from '@src/utils/timeFunctions';
import { useAxiosClient } from '@src/clients/backendClient';
import { useInfiniteQuery } from '@tanstack/react-query';
import { PagedResult } from '@src/model';
import { SortingState } from '@tanstack/react-table';
import { useGitStatsContext } from './gitStatsViewModel';

type RepoStat = {
    id: number;
    name: string;
    count: number;
    avg_loc: number;
    sum_loc: number;
    max_loc: number;
    count_repos: number;
    avg_duration: number;
    max_duration: number;
};


interface ReposStatsModel {
    reposStatsQuery: ReturnType<typeof useInfiniteQuery<PagedResult<RepoStat>>>;
    setSorting: (sorting: SortingState) => void;
}

export const useReposStatsModel = (): ReposStatsModel => {    
    const {timeFilter, managerFilter, setManagerFilter} = useGitStatsContext();
    const { topManager } = useOrgProviderContext();
    const backendClient = useAxiosClient();
    const [sorting, setSorting] = useState<SortingState>([]);

    useEffect(() => {
        if (topManager && topManager.id) {
            setManagerFilter(topManager.id);
        }
    }, [topManager]);

    const {startDate, endDate} = useTimeFilterDates(timeFilter);

    const fetchReposStatsAsync = useCallback(async (pageAfter: any, pageBefore: any, limit?:number, sorting?:SortingState) : Promise<PagedResult<RepoStat>> => {
        try {
            let managerFilterStr = '';
            if(managerFilter) {
                managerFilterStr = `&manager_id=${managerFilter}`;
            }

            let args = '';
            if (!!pageAfter) {
                args = `&after=${pageAfter}`;
            } else if (!!pageBefore) {
                args = `&before=${pageBefore}`;
            }

            let sortingArgs = '';
            if (!!sorting?.length) {
                sortingArgs = `&s=${sorting[0].id}&so=${sorting[0].desc ? 'desc' : 'asc'}`;
            }

            const response = await backendClient(`/api/git/repo_stats?page_size=${limit??30}&start_date=${startDate}&end_date=${endDate}${args}${managerFilterStr}${sortingArgs}`);
            const result = await response.data;

            if (!result.data?.length) {
                return {
                    data: [],
                    before: null,
                    after: null,
                    totalCount: 0
                };
            }

            return result;
        } catch (error) {
            console.error('Error fetching stats', error);
        }

        return {
            data: [],
            before: null,
            after: null,
            totalCount: 0
        };
    }, [startDate, endDate, managerFilter, backendClient]);

    const reposStatsQuery = useInfiniteQuery<PagedResult<RepoStat>>({
        queryKey: ['repostats', sorting, managerFilter, timeFilter],
        queryFn: async ({ pageParam }) => {      
          const fetchedData = await fetchReposStatsAsync(pageParam, undefined, 20, sorting);
          return fetchedData;
        },
        initialPageParam: "",
        getNextPageParam: (lastPage) => lastPage.after,
        refetchOnWindowFocus: false,
      })

    return {
        reposStatsQuery,
        setSorting,
    };
};


// Create the context
const ReposStatsContext: React.Context<ReposStatsModel | null> = createContext<ReposStatsModel | null>(null);

// Create a custom hook to access the context
export const useReposStatsContext = (): ReposStatsModel => {
    const context = useContext(ReposStatsContext);
    if (!context) {
        throw new Error('useDashboardContext must be used within a DashboardProvider');
    }
    return context;
};

// Create the provider component
export const RepoStatsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const model = useReposStatsModel();

    return <ReposStatsContext.Provider value={model}>
        {children}
    </ReposStatsContext.Provider>
};