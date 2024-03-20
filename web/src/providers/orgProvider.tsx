import { Team, User } from '@src/model';
import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

interface OrgDataModel {
    users: User[];
    teams: Team[];
    managers: User[];
    topManager: User | undefined;
    fetchUsersAsync: () => Promise<User>;
    levels: { managers:string[], ics:string[]}
}

const levels = {
    managers:["L4", "L5", "L6", "L7","L8", "L9"], 
    ics:["IC1", "IC2", "IC3", "IC4", "IC5", "IC6", "IC7","IC8", "IC9"]
};

export const useOrgDataModel = (): OrgDataModel => {
    const [users, setUsers] = useState<User[]>([]);
    const [teams, setTeams] = useState<Team[]>([]);
    const [managers, setManagers] = useState<User[]>([]);
    
    const fetchUsersAsync = async () => {
        try {
            const response = await fetch('/api/users?page_size=1000');
            const result = await response.json();
            const data = result.data;
            setUsers(data);
            const managers = data.filter((user: User) => user.isManager).sort((a: User, b: User) => b.level?.localeCompare(a.level ?? '')) ?? false;
            setManagers(managers);
            return data;
        } catch (error) {
            console.error('Error fetching users', error);
        }
    };

    const fetchTeamsAsync = async () => {
        try {
            const response = await fetch('/api/teams?page_size=1000');
            const result = await response.json();
            const data = result.data;
            setTeams(data);
        } catch (error) {
            console.error('Error fetching users', error);
        }
    };

    const topManager = useMemo(()=>managers.find((manager) => manager.managerId === manager.id), [managers]);

    useEffect(() => {
        fetchUsersAsync();
        fetchTeamsAsync();
    }, []);

    return {
        users,
        teams,
        managers,
        topManager,
        fetchUsersAsync,
        levels
    };
}

// Create the context for the user data
const UserDataContext = createContext<OrgDataModel | null>(null);

// Create the provider component
export const UserDataProvider:  React.FC<{ children: React.ReactNode }> = ({ children }) => {

    const model = useOrgDataModel();
    return (
        <UserDataContext.Provider value={model}>
            {children}
        </UserDataContext.Provider>
    );
};

// Create the useUsersDataModel hook
export const useOrgProviderContext = () => {
    const context = useContext(UserDataContext);
    if (!context) {
        throw new Error('useUsersProviderContext must be used within a UserDataProvider');
    }

    return context;
};



