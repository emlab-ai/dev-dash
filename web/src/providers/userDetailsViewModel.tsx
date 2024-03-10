import { useCallback, useEffect, useMemo, useState, createContext, useContext } from 'react';

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
}

export const useUserDetailsModel = (id:number): UserDetailsModel => {
    const currentDate = new Date().toISOString().split('T')[0];
    const [timeFilter, setTimeFilter] = useState('1month');    
    const [user, setUser] = useState<User | null>(null);
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


    useEffect(() => {
        fetchUserDetailsAsync(id, startDateStr, endDateStr);
    }, [id, endDateStr, startDateStr])

    return {
        timeFilter,
        setTimeFilter,
        userPrsChart,
        user
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