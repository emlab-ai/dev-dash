import { useAxiosClient } from "@src/clients/backendClient";
import { User } from "@src/model";
import useDebounceCallback from "@src/utils/debounce";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export const useUsersSettingsModel = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [usersBefore, setUsersBefore] = useState<string | null>(null);
    const [usersAfter, setUsersAfter] = useState<string | null>(null);
    const searchParams = new URLSearchParams(location.search);
    const [cursor, setCursor] = useState(searchParams.get('cursor') as string | undefined ?? "");
    const navigate = useNavigate();
    const backendClient = useAxiosClient();
    const [userFilter, setUserFilter] = useState<string | undefined>();

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

    const fetchUsersAsync = useDebounceCallback(async (before?: string, after?: string, userFilter?: string) => {
        try {
            let pageStr = '';
            if (!!before) {
                pageStr = `&before=${before}`;
            } else if (!!after) {
                pageStr = `&after=${after}`;
            }            

            if (userFilter) {
                pageStr += `&filter=${userFilter}`;
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
    }, 300, [backendClient]);

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

    useEffect(() => {
        if (userFilter !== undefined){
            fetchUsersAsync(undefined, undefined, userFilter);
        }

    }, [userFilter, fetchUsersAsync]);

    const updateUserAsync = useCallback(async (user: User) => {
        const response = await backendClient('/api/users', {
            method: 'PUT',
            headers:
                { 'Content-Type': 'application/json' },
            data: JSON.stringify(user)
        });
        const result = await response.data;

        setUsers((users) => {
            const index = users.findIndex(u => u.id === user.id);
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
        fetchUsersAsync(undefined, cursor, userFilter);
    }, [cursor, fetchUsersAsync, userFilter])

    useEffect(() => {
        refreshAsync();
    }, []);

    const nextPage = useCallback(async () => {
        if (!usersAfter) {
            return;
        }
        fetchUsersAsync(undefined, usersAfter, userFilter);
    }, [usersAfter, fetchUsersAsync, userFilter]);

    const prevPage = useCallback(async () => {
        if (!usersBefore) {
            return;
        }

        fetchUsersAsync(usersBefore, undefined, userFilter);
    }, [usersBefore, fetchUsersAsync, userFilter]);

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
        userFilter, 
        setUserFilter,
        cursor
    };
};

type UsersSettingsModel = ReturnType<typeof useUsersSettingsModel>;

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