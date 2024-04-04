import { useCallback, useEffect, useState, createContext, useContext } from 'react';
import { useOrgProviderContext } from './orgProvider';
import { useTimeFilterDates } from '@src/utils/timeFunctions';
import { User } from '@src/model';
import { useAxiosClient } from '@src/clients/backendClient';

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
    managerFilter: string;
    setTimeFilter: (timeFilter: string) => void;
    setManagerFilter: (managerFilter: string) => void;
    fetchStatsAsync: () => Promise<void>;
}

export const useDashboardModel = (): DashboardModel => {
    const { users, managers, topManager } = useOrgProviderContext();
    const [timeFilter, setTimeFilter] = useState('1month');
    const [managerFilter, setManagerFilter] = useState(topManager?.id ?? '');
    const [stats, setStats] = useState(initialStats);
    const backendClient = useAxiosClient();

    useEffect(() => {
        if (topManager && topManager.id) {
            setManagerFilter(topManager.id);
        }
    }, [topManager]);

    const {startDate, endDate} = useTimeFilterDates(timeFilter);

    const fetchStatsAsync = useCallback(async () => {
        try {
            let managerFilterStr= '';
            if (managerFilter) {
                managerFilterStr = `&manager_id=${managerFilter}`;
            }

            const response = await backendClient(`/api/stats?start_date=${startDate}&end_date=${endDate}${managerFilterStr}`);
            const data = await response.data;
            setStats({
                loaded: true,
                cues: data.cues,
                lineCharts: data.lineCharts
            });
        } catch (error) {
            console.error('Error fetching stats', error);
        }
    }, [managerFilter, startDate, endDate, backendClient]);


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