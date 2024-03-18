import { useCallback, useEffect, useMemo, useState, createContext, useContext } from 'react';
import { useOrgProviderContext } from './orgProvider';
import { useTimeFilterDates } from '@src/utils/timeFunctions';
import { useSearchStateParams } from '@src/utils/routeHooks';
import { useInfiniteQuery } from '@tanstack/react-query';
import { SortingState } from '@tanstack/react-table';


export type PullRequest = {
    id:number;
    author:string;
    authorId:number;
    prId:string;
    number:number;
    closedAt:Date;
    createdAt: Date;
    changedFiles:number;
    deletions:number;
    additions:number;
    bodyText:string;
    title:string;
    commitsCount:number;
    firstCommitMessage:string;
    firstCommitDate: Date;
    repositoryName:string;
    repositoryUrl:string;
    reviewThreadsCount:number;
    resolvedCommentsCount:number;
    commentsCount:number;
    reactionsCount:number;
    url:string;
    author_name:string;
    totalDuration:number;
};

interface PagedResult<Data extends object> {
    data: Data[];
    before: string | null;
    after: string | null;
    total_count: number;
}

interface PullRequestsModel {
    pullRequests: PullRequest[];
    totalCount: number;
    timeFilter: string;
    managerFilter: number;
    pullRequestsStats: PullRequestsStats | null;
    setTimeFilter: (timeFilter: string) => void;
    setManagerFilter: (managerFilter: number) => void;
    fetchPullRequestsAsync: (pageAfter: any, pageBefore: any, limit: any, sorting: any) => Promise<PagedResult<PullRequest>>;
    nextPage: () => Promise<void>;
    prevPage: () => Promise<void>;
    hasNextPage: boolean;
    hasPrevPage: boolean;
    pullRequestQuery: ReturnType<typeof useInfiniteQuery<PullRequest>>;
}

interface PullRequestsStats {
    avg_loc: number;
    avg_duration: number;
    avg_files_changed: number;
    avg_comments_count: number;
}

export const usePullRequestsModel = (): PullRequestsModel => {
    const [timeFilter, setTimeFilter] = useSearchStateParams("timerange", "1month");  
    const { topManager } = useOrgProviderContext();
    const [managerFilter, setManagerFilter] = useState(topManager?.id ?? 0);
    const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
    const [pullRequestsStats, setPullRequestStats] = useState<PullRequestsStats|null>(null);
    const [pageBefore, setPageBefore] = useState(null);
    const [pageAfter, setPageAfter] = useState(null);
    const [totalCount, setTotalCount] = useState(0);

    useEffect(() => {
        if (topManager) {
            setManagerFilter(topManager.id);
        }
    }, [topManager]);

    const {startDate, endDate} = useTimeFilterDates(timeFilter);

    const fetchPullRequestsAsync = useCallback(async (pageAfter: any, pageBefore: any, limit?:number, sorting?:SortingState) : Promise<PagedResult<PullRequest>> => {
        try {
            if(managerFilter === 0) {
                return {
                    data: [],
                    before: null,
                    after: null,
                    total_count: 0
                };
            }

            let args = '';
            if (!!pageAfter) {
                args = `&after=${pageAfter}`;
            } else if (!!pageBefore) {
                args = `&before=${pageBefore}`;
            }
            const response = await fetch(`http://localhost:8080/api/git/prs?page_size=30${args}&start_date=${startDate}&end_date=${endDate}&manager_id=${managerFilter}`);
            const result = await response.json();
            if (!result.data?.length) {
                return {
                    data: [],
                    before: null,
                    after: null,
                    total_count: 0
                };
            }

            // setPullRequests(result.data);
            // setPageBefore(result.before);
            // setPageAfter(result.after);
            // setTotalCount(result.total_count);

            return result;
        } catch (error) {
            console.error('Error fetching stats', error);
        }

        return {
            data: [],
            before: null,
            after: null,
            total_count: 0
        };
    }, [startDate, endDate, managerFilter]);

    const fetchPullRequestsStatsAsync = useCallback(async () => {
        try {
            if(managerFilter === 0) {
                return;
            }
            const response = await fetch(`http://localhost:8080/api/git/prs_stats?start_date=${startDate}&end_date=${endDate}&manager_id=${managerFilter}`);
            const result = await response.json();
          
            setPullRequestStats(result);
        } catch (error) {
            console.error('Error fetching stats', error);
        }
    }, [startDate, endDate, managerFilter]);



    useEffect(() => {
        fetchPullRequestsAsync(null, null);
        fetchPullRequestsStatsAsync();
    }, [managerFilter, timeFilter])

    const nextPage = useCallback(async () => {
        await fetchPullRequestsAsync(pageAfter, null);
    }, [pageAfter]);

    const prevPage = useCallback(async () => {
        await fetchPullRequestsAsync(null, pageBefore);
    }, [pageBefore]);

    const {sorting, setSorting} = useState<SortingState>([]);
    
    const pullRequestQuery = useInfiniteQuery<PullRequest>({
        queryKey: ['people', sorting, managerFilter, timeFilter],
        queryFn: async ({ pageParam }) => {      
          const fetchedData = await fetchPullRequestsAsync(pageParam, undefined, 20, sorting);
          return fetchedData;
        },
        initialPageParam: "",
        getNextPageParam: (lastPage, pages) => lastPage.after,
        refetchOnWindowFocus: false,
      })

    return {
        timeFilter,
        setTimeFilter,
        managerFilter,
        setManagerFilter,
        pullRequests,
        fetchPullRequestsAsync,
        totalCount,
        nextPage,
        prevPage,
        pullRequestQuery,
        pullRequestsStats,
        hasNextPage: !!pageAfter,
        hasPrevPage: !!pageBefore
    };
};


// Create the context
const PullRequestsContext: React.Context<PullRequestsModel | null> = createContext<PullRequestsModel | null>(null);

// Create a custom hook to access the context
export const usePullRequestsContext = (): PullRequestsModel => {
    const context = useContext(PullRequestsContext);
    if (!context) {
        throw new Error('useDashboardContext must be used within a DashboardProvider');
    }
    return context;
};

// Create the provider component
export const PullRequestsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const model = usePullRequestsModel();

    return <PullRequestsContext.Provider value={model}>
        {children}
    </PullRequestsContext.Provider>
};