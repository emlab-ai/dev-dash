import { useMsal } from '@azure/msal-react';
import { apiRequest } from '@src/authConfig';
import React, { createContext, useContext, useEffect, useState } from 'react';

// Define the shape of the AuthContext value
interface AuthContextValue {
    isAuthenticated: boolean;
    token: string;
}

const useAuthContextValue = (): AuthContextValue => {
    const { instance, accounts } = useMsal();
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [token, setToken] = useState('');

    useEffect(() => {
        if (accounts.length > 0) {
            const request = {
                ...apiRequest,
                account: accounts[0] // Assuming the user is logged in, accounts[0] is their account
            }; 

            instance.initialize().then(() => {
                return instance.acquireTokenSilent(request).then((response) => {
                    setToken(response.accessToken);
                    setIsAuthenticated(true);
                })
        }).catch((error) => {
                console.error('Error acquiring token', error);
                // TODO: use Error Context
            });
        }
    }, [accounts]);

    return {
        isAuthenticated,
        token
    }
}

// Create the AuthContext
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// Create the AuthContextProvider component
const AuthContextProvider: React.FC<any> = ({ children }) => {
    const authContextValue = useAuthContextValue();
    // Add your authentication-related state and functions here

    return <AuthContext.Provider value={authContextValue}>{children}</AuthContext.Provider>;
};

// Create the useAuth hook
const useAuth = (): AuthContextValue => {
    const authContext = useContext(AuthContext);

    if (!authContext) {
        throw new Error('useAuth must be used within an AuthContextProvider');
    }

    return authContext;
};

export { AuthContext, AuthContextProvider, useAuth };