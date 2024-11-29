import { createContext, useContext } from 'react';


interface UserModel {
}

export const useUserModel = (): UserModel => {    
    return {
        
    };
};


const UserContext: React.Context<UserModel | null> = createContext<UserModel | null>(null);

export const useUserContext = (): UserModel => {
    const context = useContext(UserContext);
    if (!context) {
        throw new Error('useDashboardContext must be used within a DashboardProvider');
    }
    return context;
};

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const model = useUserModel();

    return <UserContext.Provider value={model}>
        {children}
    </UserContext.Provider>
};