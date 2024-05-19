import { useEffect, useState, createContext, useContext } from 'react';
import { useOrgProviderContext } from './orgProvider';
import { useSearchStateParams } from '@src/utils/routeHooks';


interface GitStatsModel {
    timeFilter: string;
    managerFilter?: number;
    setTimeFilter: (timeFilter: string) => void;
    setManagerFilter: (managerFilter?: number) => void;
}

export const useGitStatsModel = (): GitStatsModel => {
    const [timeFilter, setTimeFilter] = useSearchStateParams("timerange", "1month");  
    const { topManager } = useOrgProviderContext();
    const [managerFilter, setManagerFilter] = useState(topManager?.id);
   
    useEffect(() => {
        if (topManager && topManager.id) {
            setManagerFilter(topManager.id);
        }
    }, [topManager]);


    return {
        timeFilter,
        setTimeFilter,
        managerFilter,
        setManagerFilter,       
    };
};


// Create the context
const GitStatsContext: React.Context<GitStatsModel | null> = createContext<GitStatsModel | null>(null);

// Create a custom hook to access the context
export const useGitStatsContext = (): GitStatsModel => {
    const context = useContext(GitStatsContext);
    if (!context) {
        throw new Error('useGitStatsContext must be used within a GitStatsProvider');
    }

    return context;
};

// Create the provider component
export const GitStatsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const model = useGitStatsModel();

    return <GitStatsContext.Provider value={model}>
        {children}
    </GitStatsContext.Provider>
};