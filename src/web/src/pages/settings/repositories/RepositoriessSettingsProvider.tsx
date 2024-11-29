import { useAxiosClient } from "@src/clients/backendClient";
import { RepositorySettings } from "@src/model";
import { createContext, useCallback, useContext, useEffect, useState } from "react";

const useRepoSettingsModel = () => {
    const [repoSettings, setRepoSettings] = useState<RepositorySettings[]>([]);
    const [reposBefore, setReposBefore] = useState<string|null>(null);
    const [reposAfter, setReposAfter] = useState<string|null>(null);
    const axiosFetch = useAxiosClient();

    const fetchRepoSettingsAsync = useCallback(async (before?: string, after?: string) => {
        try {
            let pageStr = '';
            if (before) {
                pageStr = `&before=${before}`;
            } else if (after) {
                pageStr = `&after=${after}`;
            }
            const response = await axiosFetch(`/api/repoSettings?page_size=20${pageStr}`);
            const result = await response.data;

            setRepoSettings(result.data);
            setReposBefore(result.before);
            setReposAfter(result.after);
        } catch (error) {
            console.error('Error fetching reviews', error);
        }
    }, [axiosFetch]);


    const createRepoSettingsAsync = useCallback(async (repo: RepositorySettings) => {
        const response = await axiosFetch('/api/repoSettings', {
            method: 'POST',
            headers: 
                {'Content-Type': 'application/json'},
            data: JSON.stringify(repo)
        });
        const result = await response.data;
        setRepoSettings((repos)=>[...repos, result]);
    }, [axiosFetch, setRepoSettings])


    const updateRepoSettingsAsync = useCallback(async (rs: RepositorySettings) => {
        const response = await axiosFetch('/api/repoSettings', {
            method: 'PUT',
            headers: 
                {'Content-Type': 'application/json'},
            data: JSON.stringify(rs)
        });

        const result = await response.data;
        
        setRepoSettings((repos)=>{
            const index = repos.findIndex(u=>u.id === rs.id);        
            const res = repos.splice(0);
            res[index] =  result;
            return res;
        });
    }, [setRepoSettings, axiosFetch])


    const deleteRepoSettingsAsync = useCallback(async (repoSettingsId: number) => {
        const response = await axiosFetch(`/api/repoSettings/${repoSettingsId}`, {
            method: 'DELETE'
        });
        
        if (response.status !== 204) {
            console.error('Error deleting repository settings');
            return;
        }
        setRepoSettings((repos)=>repos.filter(t=>t.id !== repoSettingsId));
    }, [axiosFetch]);

    useEffect(() => {
        fetchRepoSettingsAsync();
    }, [])

   
    const nextPage = useCallback(async () => {
        if (!reposAfter) {
            return;
        }
        fetchRepoSettingsAsync(undefined, reposAfter);
    }, [reposAfter, fetchRepoSettingsAsync]);

    const prevPage = useCallback(async () => {
        if (!reposBefore) {
            return;
        }
        fetchRepoSettingsAsync(reposBefore);
    }, [reposBefore, fetchRepoSettingsAsync]);

    return {
        repoSettings,
        nextPage: nextPage,
        prevPage: prevPage,
        hasNext: !!reposAfter,
        hasPrev: !!reposBefore,
        createRepoSettingsAsync,
        deleteRepoSettingsAsync,
        updateRepoSettingsAsync
    };
};

type RepoSettingsModel = ReturnType<typeof useRepoSettingsModel>;

// Create the context
const RepoSettingsContext: React.Context<RepoSettingsModel | null> = createContext<RepoSettingsModel | null>(null);

// Create a custom hook to access the context
export const useRepoSettingsContext = (): RepoSettingsModel => {
    const context = useContext(RepoSettingsContext);
    if (!context) {
        throw new Error('useDashboardContext must be used within a DashboardProvider');
    }
    return context;
};

// Create the provider component
export const RepoSettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const model = useRepoSettingsModel();

    return <RepoSettingsContext.Provider value={model}>
        {children}
    </RepoSettingsContext.Provider>
};