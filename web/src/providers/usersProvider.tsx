import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

// Define the user data model
export interface UserData {
    id: number;
    managerId:number;
    name: string;
    email: string;
    isManager: boolean;
    gitAlias: string;
    level:string;
}


interface UserDataModel {
    users: UserData[];
    managers: UserData[];
    topManager: UserData | undefined;
    fetchUsersAsync: () => Promise<UserData>;
}

export const useUserDataModel = (): UserDataModel => {
    const [users, setUsers] = useState<UserData[]>([]);
    const [managers, setManagers] = useState<UserData[]>([]);
    
    const fetchUsersAsync = async () => {
        try {
            const response = await fetch('http://localhost:8080/api/users');
            const data = await response.json();
            setUsers(data);
            const managers = data.filter((user: UserData) => user.isManager).sort((a: UserData, b: UserData) => b.level.localeCompare(a.level));
            setManagers(managers);
            return data;
        } catch (error) {
            console.error('Error fetching users', error);
        }
    };

    const topManager = useMemo(()=>managers.find((manager) => manager.managerId === manager.id), [managers]);

    useEffect(() => {
        fetchUsersAsync();
    }, []);

    return {
        users,
        managers,
        topManager,
        fetchUsersAsync
    };
}

// Create the context for the user data
const UserDataContext = createContext<UserDataModel | null>(null);

// Create the provider component
export const UserDataProvider:  React.FC<{ children: React.ReactNode }> = ({ children }) => {

    const model = useUserDataModel();
    return (
        <UserDataContext.Provider value={model}>
            {children}
        </UserDataContext.Provider>
    );
};

// Create the useUsersDataModel hook
export const useUsersProviderContext = () => {
    const context = useContext(UserDataContext);
    if (!context) {
        throw new Error('useUsersProviderContext must be used within a UserDataProvider');
    }

    return context;
};



