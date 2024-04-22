import { useAxiosClient } from "@src/clients/backendClient";
import { User } from "@src/model";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

interface UsersSettingsModel {
    users: User[];
    nextPage: () => void;
    prevPage: () => void;
    hasNext: boolean;
    hasPrev: boolean;
    createUserAsync: (user: User) => Promise<void>;
    deleteUserAsync: (userId: number) => Promise<void>;
    updateUserAsync: (user: User) => Promise<void>;
    refreshAsync: () => Promise<void>;
    cursor: string;
}

export const useUsersSettingsModel = (): UsersSettingsModel => {
    const [users, setUsers] = useState<User[]>([]);
    const [usersBefore, setUsersBefore] = useState<string | null>(null);
    const [usersAfter, setUsersAfter] = useState<string | null>(null);
    const searchParams = new URLSearchParams(location.search);
    const [cursor, setCursor] = useState(searchParams.get('cursor') as string | undefined ?? "");
    const navigate = useNavigate();
    const backendClient = useAxiosClient();


    useEffect(() => {
        const searchParams = new URLSearchParams(location.search);

        if (cursor) {
            searchParams.set('cursor', cursor);
        } else {
            searchParams.delete('cursor');
        }

        navigate({
            pathname: location.pathname,
            search: searchParams.toString(),
        });
    }, [cursor, navigate]);

    const fetchUsersAsync = useCallback(async (before?: string, after?: string) => {
        try {
            let pageStr = '';
            if (!!before) {
                pageStr = `&before=${before}`;
            } else if (!!after) {
                pageStr = `&after=${after}`;
            }
            const response = await backendClient(`/api/users?page_size=20${pageStr}`);
            const result = await response.data;

            setUsers(result.data);
            setUsersBefore(result.before);
            setCursor(result.before);
            setUsersAfter(result.after);
        } catch (error) {
            console.error('Error fetching reviews', error);
        }
    }, [backendClient]);

    const createUserAsync = useCallback(async (user: User) => {
        const response = await backendClient('/api/users', {
            method: 'POST',
            headers:
                { 'Content-Type': 'application/json' },
            data: JSON.stringify(user)
        });
        const result = await response.data;
        setUsers((users) => [...users, result]);
    }, [backendClient, setUsers]);

    const updateUserAsync = useCallback(async (user: User) => {
        const response = await backendClient('/api/users', {
            method: 'PUT',
            headers:
                { 'Content-Type': 'application/json' },
            data: JSON.stringify(user)
        });
        const result = await response.data;

        setUsers((users) => {
            var index = users.findIndex(u => u.id === user.id);
            const res = users.splice(0);
            res[index] = result;
            return res;
        });
    }, [users, backendClient, setUsers]);

    const deleteUserAsync = useCallback(async (userId: number) => {
        const response = await backendClient(`/api/users/${userId}`, {
            method: 'DELETE'
        });
        
        if (response.status !== 204) {
            console.error('Error deleting a user');
            return;
        }
        setUsers((users) => users.filter(t => t.id !== userId));
    }, [backendClient, setUsers]);

    const refreshAsync = useCallback(async () => {
        fetchUsersAsync(undefined, cursor);
    }, [cursor, fetchUsersAsync])

    useEffect(() => {
        refreshAsync();
    }, [])

    const nextPage = useCallback(async () => {
        if (!usersAfter) {
            return;
        }
        fetchUsersAsync(undefined, usersAfter);
    }, [usersAfter, fetchUsersAsync]);

    const prevPage = useCallback(async () => {
        if (!usersBefore) {
            return;
        }
        fetchUsersAsync(usersBefore);
    }, [usersBefore, fetchUsersAsync]);

    return {
        users,
        nextPage,
        prevPage,
        hasNext: !!usersAfter,
        hasPrev: !!usersBefore,
        refreshAsync,
        createUserAsync,
        deleteUserAsync,
        updateUserAsync,
        cursor
    };
};


// Create the context
const UsersSettingsContext: React.Context<UsersSettingsModel | null> = createContext<UsersSettingsModel | null>(null);

// Create a custom hook to access the context
export const useUsersSettingsContext = (): UsersSettingsModel => {
    const context = useContext(UsersSettingsContext);
    if (!context) {
        throw new Error('useDashboardContext must be used within a DashboardProvider');
    }
    return context;
};

// Create the provider component
export const UsersSettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const model = useUsersSettingsModel();

    return <UsersSettingsContext.Provider value={model}>
        {children}
    </UsersSettingsContext.Provider>
};