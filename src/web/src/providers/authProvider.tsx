import { useAuth0 } from '@auth0/auth0-react';
import React, { createContext, useContext, useEffect, useState } from 'react';

// Define the shape of the AuthContext value
interface AuthContextValue {
    isAuthenticated: boolean;
    token: string;
}

const useAuthContextValue = (): AuthContextValue => {
    const { getAccessTokenSilently, isAuthenticated } = useAuth0();
    const [token, setToken] = useState('');

    useEffect(() => {
        const getToken = async () => {
          if (isAuthenticated) {
            try {
              const accessToken = await getAccessTokenSilently({

                authorizationParams:{
                    audience: "https://emlab.ai/api/",
                    scope: "openid profile email"
                }
              });
              setToken(accessToken);
            } catch (error) {
              console.error(error);
            }
          }
        };
    
        getToken();
      }, [isAuthenticated, getAccessTokenSilently]);

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