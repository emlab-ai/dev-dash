import { useAxiosClient } from "@src/clients/backendClient";
import { Team } from "@src/model";
import { createContext, useCallback, useContext, useEffect, useState } from "react";

interface TeamsSettingsModel {
    teams: Team[];
    nextPage: () => void;
    prevPage: () => void;
    hasNext: boolean;
    hasPrev: boolean;
    createTeamAsync: (team: Team) => Promise<void>;
    deleteTeamAsync: (teamId: string) => Promise<void>;
    updateTeamAsync: (team: Team) => Promise<void>;
}

export const useTeamsSettingsModel = (): TeamsSettingsModel => {
    const [teams, setTeams] = useState<Team[]>([]);
    const [teamsBefore, setTeamsBefore] = useState<string|null>(null);
    const [teamsAfter, setTeamsAfter] = useState<string|null>(null);
    const backendClient = useAxiosClient();

    const fetchTeamsAsync = useCallback(async (before?: string, after?: string) => {
        try {
            let pageStr = '';
            if (!!before) {
                pageStr = `&before=${before}`;
            } else if (!!after) {
                pageStr = `&after=${after}`;
            }
            const response = await backendClient(`/api/teams?page_size=20${pageStr}`);
            const result = await response.data;

            setTeams(result.data);
            setTeamsBefore(result.before);
            setTeamsAfter(result.after);
        } catch (error) {
            console.error('Error fetching reviews', error);
        }
    }, [backendClient]);


    const createTeamAsync = useCallback(async (team: Team) => {
        var requestInfo = {
            method: 'POST',
            headers: 
                {'Content-Type': 'application/json'},
            body: JSON.stringify(team)
        };

        const response = await backendClient('/api/teams', requestInfo);
        const result = await response.data;
        setTeams((teams)=>[...teams, result]);
    }, [backendClient, setTeams])


    const updateTeamAsync = useCallback(async (team: Team) => {
        var requestInfo = {
            method: 'PUT',
            headers: 
                {'Content-Type': 'application/json'},
            body: JSON.stringify(team)
        };

        const response = await backendClient('/api/teams', requestInfo);
        const result = await response.data;
        
        setTeams((teams)=>{
            var index = teams.findIndex(u=>u.id === team.id);        
            const res = teams.splice(0);
            res[index] =  result;
            return res;
        });
    }, [teams, backendClient])


    const deleteTeamAsync = useCallback(async (teamId: string) => {
        var requestInfo = {
            method: 'DELETE'
        };

        const response = await backendClient(`/api/teams/${teamId}`, requestInfo);
        if (response.status !== 204) {
            console.error('Error deleting team');
            return;
        }
        setTeams((teams)=>teams.filter(t=>t.id !== teamId));
    }, [backendClient]);

    useEffect(() => {
        fetchTeamsAsync();
    }, [fetchTeamsAsync])

   
    const nextPage = useCallback(async () => {
        if (!teamsAfter) {
            return;
        }
        fetchTeamsAsync(undefined, teamsAfter);
    }, [teamsAfter, fetchTeamsAsync]);

    const prevPage = useCallback(async () => {
        if (!teamsBefore) {
            return;
        }
        fetchTeamsAsync(teamsBefore);
    }, [teamsBefore, fetchTeamsAsync]);

    return {
        teams,
        nextPage: nextPage,
        prevPage: prevPage,
        hasNext: !!teamsAfter,
        hasPrev: !!teamsBefore,
        createTeamAsync,
        deleteTeamAsync,
        updateTeamAsync
    };
};


// Create the context
const TeamsSettingsContext: React.Context<TeamsSettingsModel | null> = createContext<TeamsSettingsModel | null>(null);

// Create a custom hook to access the context
export const useTeamsSettingsContext = (): TeamsSettingsModel => {
    const context = useContext(TeamsSettingsContext);
    if (!context) {
        throw new Error('useDashboardContext must be used within a DashboardProvider');
    }
    return context;
};

// Create the provider component
export const TeamsSettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const model = useTeamsSettingsModel();

    return <TeamsSettingsContext.Provider value={model}>
        {children}
    </TeamsSettingsContext.Provider>
};