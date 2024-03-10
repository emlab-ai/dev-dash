import { useCallback, useEffect, useMemo, useState, createContext, useContext } from 'react';
import { useUsersProviderContext } from './usersProvider';


type User = {
    id: string;
    name: string;
    managerId: string;
    team: string;
    isManager: boolean;
};


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
    totalDuration:number;
};



interface PullRequestsModel {
    pullRequests: PullRequest[];
    totalCount: number;
    timeFilter: string;
    managerFilter: number;
    pullRequestsStats: PullRequestsStats | null;
    setTimeFilter: (timeFilter: string) => void;
    setManagerFilter: (managerFilter: number) => void;
    fetchPullRequestsAsync: (pageAfter: any, pageBefore: any) => Promise<void>;
    nextPage: () => Promise<void>;
    prevPage: () => Promise<void>;
    hasNextPage: boolean;
    hasPrevPage: boolean;
}

interface PullRequestsStats {
    avg_loc: number;
    avg_duration: number;
    avg_files_changed: number;
    avg_comments_count: number;
}

export const usePullRequestsModel = (): PullRequestsModel => {
    const currentDate = new Date().toISOString().split('T')[0];
    const [timeFilter, setTimeFilter] = useState('1month');    
    const { topManager } = useUsersProviderContext();
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

    const startDateStr = useMemo(() => {
        let date = new Date(currentDate);
        switch (timeFilter) {
            case '1month':
                date.setMonth(date.getMonth() - 1);
                break;
            case '6months':
                date.setMonth(date.getMonth() - 6);
                break;
            case '12months':
                date.setFullYear(date.getFullYear() - 1);
                break;
            default:
                break;
        }
        return date.toISOString().split('T')[0];
    }, [timeFilter]);

    const endDate = new Date(currentDate);
    endDate.setDate(endDate.getDate() + 1);
    const endDateStr = endDate.toISOString().split('T')[0];

    const fetchPullRequestsAsync = useCallback(async (pageAfter: any, pageBefore: any) => {
        try {
            if(managerFilter === 0) {
                return;
            }

            let args = '';
            if (!!pageAfter) {
                args = `&after=${pageAfter}`;
            } else if (!!pageBefore) {
                args = `&before=${pageBefore}`;
            }
            const response = await fetch(`http://localhost:8080/api/git/prs?page_size=30${args}&start_date=${startDateStr}&end_date=${endDateStr}&manager_id=${managerFilter}`);
            const result = await response.json();
            if (!result.data?.length) {
                return;
            }

            setPullRequests(result.data);
            setPageBefore(result.before);
            setPageAfter(result.after);
            setTotalCount(result.total_count);
        } catch (error) {
            console.error('Error fetching stats', error);
        }
    }, [startDateStr, endDateStr, managerFilter]);

    const fetchPullRequestsStatsAsync = useCallback(async () => {
        try {
            if(managerFilter === 0) {
                return;
            }
            const response = await fetch(`http://localhost:8080/api/git/prs_stats?start_date=${startDateStr}&end_date=${endDateStr}&manager_id=${managerFilter}`);
            const result = await response.json();
          
            setPullRequestStats(result);
        } catch (error) {
            console.error('Error fetching stats', error);
        }
    }, [startDateStr, endDateStr, managerFilter]);



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