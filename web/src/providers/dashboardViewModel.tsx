import { useCallback, useEffect, useState, createContext, useContext, useMemo } from 'react';
import { User, useOrgProviderContext } from './orgProvider';
import { useTimeFilterDates } from '@src/utils/timeFunctions';

type StatCue = {
    label: string;
    id: string,
    loaded: boolean;
    value: number;
    diffPercent: number;
};

export type LineChartData = {
    id: string;
    title: string;
    labels: any[];
    datasets: {
        label: string;
        data: number[];
        backgroundColor: string;
        borderColor: string;
    }[];
}

type Stats = {
    loaded: boolean;
    cues: StatCue[];
    lineCharts?: LineChartData[];
};

const initialStats: Stats = {
    loaded: false,
    cues: [
       
    ]
};

interface DashboardModel {
    users: User[];
    managers: User[];
    topManager: User  | undefined;
    stats: Stats;
    timeFilter: string;
    managerFilter: number;
    setTimeFilter: (timeFilter: string) => void;
    setManagerFilter: (managerFilter: number) => void;
    fetchStatsAsync: () => Promise<void>;
}

export const useDashboardModel = (): DashboardModel => {
    const { users, managers, topManager } = useOrgProviderContext();
    const [timeFilter, setTimeFilter] = useState('1month');
    const [managerFilter, setManagerFilter] = useState(topManager?.id ?? 0);
    const [stats, setStats] = useState(initialStats);

    useEffect(() => {
        if (topManager) {
            setManagerFilter(topManager.id);
        }
    }, [topManager]);

    const {startDate, endDate} = useTimeFilterDates(timeFilter);

    const fetchStatsAsync = useCallback(async () => {
        try {
            if (managerFilter === 0) {
                return;
            }
            const response = await fetch(`http://localhost:8080/api/stats?start_date=${startDate}&end_date=${endDate}&manager_id=${managerFilter}`);
            const data = await response.json();
            setStats({
                loaded: true,
                cues: data.cues,
                lineCharts: data.lineCharts
            });
        } catch (error) {
            console.error('Error fetching stats', error);
        }
    }, [managerFilter, startDate, endDate]);


    useEffect(() => {
        fetchStatsAsync();
    }, [managerFilter, timeFilter])

    return {
        users,
        managers,
        topManager,
        timeFilter,
        setTimeFilter,
        managerFilter,
        setManagerFilter,
        stats,
        fetchStatsAsync
    };
};


// Create the context
const DashboardContext: React.Context<DashboardModel | null> = createContext<DashboardModel | null>(null);

// Create a custom hook to access the context
export const useDashboardContext = (): DashboardModel => {
    const context = useContext(DashboardContext);
    if (!context) {
        throw new Error('useDashboardContext must be used within a DashboardProvider');
    }
    return context;
};

// Create the provider component
export const DashboardProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const dashboardModel = useDashboardModel();

    return <DashboardContext.Provider value={dashboardModel}>
        {children}
    </DashboardContext.Provider>
};