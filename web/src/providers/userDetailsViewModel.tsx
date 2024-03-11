import { useCallback, useEffect, useMemo, useState, createContext, useContext } from 'react';
import { PullRequest } from './pullRequestsViewModel';

type User = {
    id: string;
    name: string;
    managerId: string;
    team: string;
    gitAlias: string;
    isManager: boolean;
};

type UserPrsChart = {
    labels: Date[];
    data: number[];
}

interface UserDetailsModel {
    user: User | null;
    timeFilter: string;
    userPrsChart: UserPrsChart | null;
    setTimeFilter: (timeFilter: string) => void;
    pullRequests: PullRequest[] | null;
    nextPullReqestPage: () => void;
    prevPullReqestPage: () => void;
    hasNextPullReqestPage: boolean;
    hasPrevPullReqestPage: boolean;
    startDate: string;
    endDate: string;
}

export const useUserDetailsModel = (id:number): UserDetailsModel => {
    const currentDate = new Date().toISOString().split('T')[0];
    const [timeFilter, setTimeFilter] = useState('1month');    
    const [user, setUser] = useState<User | null>(null);
    const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
    const [pullRequestsBefore, setPullRequestsBefore] = useState<string|null>(null);
    const [pullRequestsAfter, setPullRequestsAfter] = useState<string|null>(null);
    const [userPrsChart, setUserPrsChart] = useState<UserPrsChart | null>(null);
    

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

    const fetchUserDetailsAsync = useCallback(async (id:number, startDateStr: string, endDateStr: string) => {
        try {
            const response = await fetch(`http://localhost:8080/api/users/${id}/stats?start_date=${startDateStr}&end_date=${endDateStr}`);
            const result = await response.json();

            setUser(result.user);
            setUserPrsChart(result.prsCount);
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
        fetchUserDetailsAsync(id, startDateStr, endDateStr);
        fetchPullRequestsAsync(id, startDateStr, endDateStr);        
    }, [id, endDateStr, startDateStr])

    const nextPullRequestPage = useCallback(async () => {
        if (!pullRequestsAfter) {
            return;
        }
        fetchPullRequestsAsync(id, startDateStr, endDateStr, undefined, pullRequestsAfter);
    }, [pullRequestsAfter, id, startDateStr, endDateStr, fetchPullRequestsAsync]);

    const prevPullRequestPage = useCallback(async () => {
        if (!pullRequestsBefore) {
            return;
        }
        fetchPullRequestsAsync(id, startDateStr, endDateStr, pullRequestsBefore);
    }, [pullRequestsBefore, id, startDateStr, endDateStr,fetchPullRequestsAsync]);

   

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
        startDate: startDateStr,
        endDate: endDateStr   
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
export const UserDetailsProvider: React.FC<{ id:number, children: React.ReactNode }> = ({id, children }) => {
    const model = useUserDetailsModel(id);

    return <UserDetailsContext.Provider value={model}>
        {children}
    </UserDetailsContext.Provider>
};