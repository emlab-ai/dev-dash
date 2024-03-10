import { useCallback, useEffect, useMemo, useState, createContext, useContext } from 'react';
import { useUsersProviderContext } from './usersProvider';

type User = {
    id: string;
    name: string;
    managerId: string;
    team: string;
    gitAlias: string;
    isManager: boolean;
};

type UserStat = {
    authorId: number;
    user_name: string;
    user_team: string;
    count: number;
    avg_loc: number;
    sum_loc: number;
    max_loc: number;
    count_repos: number;
    avg_duration: number;
    max_duration: number;
};


interface UsersStatsModel {
    usersStats: UserStat[];
    timeFilter: string;
    managerFilter: number;
    setTimeFilter: (timeFilter: string) => void;
    setManagerFilter: (managerFilter: number) => void;
    fetchUserStatsAsync: () => Promise<void>;
}

export const useUsersStatsModel = (): UsersStatsModel => {
    const currentDate = new Date().toISOString().split('T')[0];
    const [timeFilter, setTimeFilter] = useState('1month');    
    const { topManager } = useUsersProviderContext();
    const [managerFilter, setManagerFilter] = useState(topManager?.id ?? 0);
    const [usersStats, setUsersStats] = useState<UserStat[]>([]);

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

    const fetchUserStatsAsync = useCallback(async () => {
        try {
            if(managerFilter === 0) {
                return;
            }

            const response = await fetch(`http://localhost:8080/api/users/stats?start_date=${startDateStr}&end_date=${endDateStr}&manager_id=${managerFilter}`);
            const result = await response.json();

            setUsersStats(result);
        } catch (error) {
            console.error('Error fetching stats', error);
        }
    }, [startDateStr, endDateStr, managerFilter]);


    useEffect(() => {
        fetchUserStatsAsync();
    }, [managerFilter, timeFilter])


    return {
        timeFilter,
        setTimeFilter,
        managerFilter,
        setManagerFilter,
        usersStats,
        fetchUserStatsAsync        
    };
};


// Create the context
const UsersStatsContext: React.Context<UsersStatsModel | null> = createContext<UsersStatsModel | null>(null);

// Create a custom hook to access the context
export const useUsersStatsContext = (): UsersStatsModel => {
    const context = useContext(UsersStatsContext);
    if (!context) {
        throw new Error('useDashboardContext must be used within a DashboardProvider');
    }
    return context;
};

// Create the provider component
export const UsersStatsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const model = useUsersStatsModel();

    return <UsersStatsContext.Provider value={model}>
        {children}
    </UsersStatsContext.Provider>
};