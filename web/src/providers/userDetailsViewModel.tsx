import { useCallback, useEffect, useMemo, useState, createContext, useContext } from 'react';
import { PullRequest } from './pullRequestsViewModel';
import { useTimeFilterDates } from '@src/utils/timeFunctions';
import { useSearchStateParams } from '@src/utils/routeHooks';

type User = {
    id: string;
    name: string;
    managerId: string;
    team: string;
    gitAlias: string;
    isManager: boolean;
};

type ChartData = {
    labels: Date[];
    data: number[];
}

interface UserDetailsModel {
    user: User | null;
    timeFilter: string;
    userPrsChart: ChartData | null;
    userReviewsChart: ChartData | null;
    setTimeFilter: (timeFilter: string) => void;
    pullRequests: PullRequest[] | null;
    nextPullReqestPage: () => void;
    prevPullReqestPage: () => void;
    hasNextPullReqestPage: boolean;
    hasPrevPullReqestPage: boolean;
    startDate: string;
    endDate: string;
}

export const useUserDetailsModel = (id?:number): UserDetailsModel => {    
    const [timeFilter, setTimeFilter] = useSearchStateParams("timerange", "1month");  
    const [user, setUser] = useState<User | null>(null);
    const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
    const [pullRequestsBefore, setPullRequestsBefore] = useState<string|null>(null);
    const [pullRequestsAfter, setPullRequestsAfter] = useState<string|null>(null);
    const [userPrsChart, setUserPrsChart] = useState<ChartData | null>(null);
    const [userReviewsChart, setUserReviewsChart] = useState<ChartData | null>(null);

    const {startDate, endDate} = useTimeFilterDates(timeFilter);

    const fetchUserDetailsAsync = useCallback(async (id:number, startDateStr: string, endDateStr: string) => {
        try {
            const response = await fetch(`http://localhost:8080/api/users/${id}/stats?start_date=${startDateStr}&end_date=${endDateStr}`);
            const result = await response.json();

            setUser(result.user);
            setUserPrsChart(result.prsCount);
            setUserReviewsChart(result.reviewsCount);
        } catch (error) {
            console.error('Error fetching stats', error);
        }
    }, []);

    const fetchPullRequestsAsync = useCallback(async (user_id:number, startDateStr: string, endDateStr: string, before?: string, after?: string) => {
        try {
            let pageStr = '';
            if (!!before) {
                pageStr = `&before=${before}`;
            } else if (!!after) {
                pageStr = `&after=${after}`;
            }
            const response = await fetch(`http://localhost:8080/api/git/prs?start_date=${startDateStr}&end_date=${endDateStr}&user_id=${user_id}&page_size=10${pageStr}`);
            const result = await response.json();

            setPullRequests(result.data);
            setPullRequestsBefore(result.before);
            setPullRequestsAfter(result.after);
        } catch (error) {
            console.error('Error fetching stats', error);
        }
    }, []);


    useEffect(() => {
        if(!id) {
            return;
        }

        fetchUserDetailsAsync(id, startDate, endDate);
        fetchPullRequestsAsync(id, startDate, endDate);        
    }, [id, endDate, startDate])

    const nextPullRequestPage = useCallback(async () => {
        if (!pullRequestsAfter || !id) {
            return;
        }
        fetchPullRequestsAsync(id, startDate, endDate, undefined, pullRequestsAfter);
    }, [pullRequestsAfter, id, startDate, endDate, fetchPullRequestsAsync]);

    const prevPullRequestPage = useCallback(async () => {
        if (!pullRequestsBefore || !id) {
            return;
        }
        fetchPullRequestsAsync(id, startDate, endDate, pullRequestsBefore);
    }, [pullRequestsBefore, id, startDate, endDate,fetchPullRequestsAsync]);

    return {
        timeFilter,
        setTimeFilter,
        userPrsChart,
        pullRequests,
        user,
        nextPullReqestPage: nextPullRequestPage,
        prevPullReqestPage: prevPullRequestPage,
        hasNextPullReqestPage: !!pullRequestsAfter,
        hasPrevPullReqestPage: !!pullRequestsBefore,
        startDate: startDate,
        endDate: endDate,
        userReviewsChart
    };
};


// Create the context
const UserDetailsContext: React.Context<UserDetailsModel | null> = createContext<UserDetailsModel | null>(null);

// Create a custom hook to access the context
export const useUserDetailsContext = (): UserDetailsModel => {
    const context = useContext(UserDetailsContext);
    if (!context) {
        throw new Error('useDashboardContext must be used within a DashboardProvider');
    }
    return context;
};

// Create the provider component
export const UserDetailsProvider: React.FC<{ id?:number, children: React.ReactNode }> = ({id, children }) => {
    const model = useUserDetailsModel(id);

    return <UserDetailsContext.Provider value={model}>
        {children}
    </UserDetailsContext.Provider>
};