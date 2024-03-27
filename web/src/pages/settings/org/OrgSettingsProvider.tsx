import { useAxiosClient } from '@src/clients/backendClient';
import { Tenant } from '@src/model';
import React, { createContext, useCallback, useEffect, useState } from 'react';

interface OrgSettingsModel {
    tenant: Tenant | undefined;
    isGithugConnected: boolean;
    startGithubConnect: () => Promise<void>;
}

export const useOrgSettingsModel = (): OrgSettingsModel => {
    const [tenant, setTenant] = useState<Tenant | undefined>();

    const axiosFetch = useAxiosClient();


    const fetchTenantAsync = useCallback(async () => {
        try {
            const response = await axiosFetch(`/api/tenant`);
            const data = await response.data;

            setTenant(data);
        } catch (error) {
            console.error('Error fetching reviews', error);
        }
    }, [axiosFetch]);

    const startGithubConnect = useCallback(async () => {
        try {
            const response = await axiosFetch(`/api/github/installation`, {
                method: 'POST'
            });
            const result = await response.data;

            if (result.state) {
                // Redirect to GitHub
                let gitUrl = "https://github.com/apps/emlab-ai/installations/new?state=" + result.state;
                window.location.href = gitUrl;
            }

        } catch (error) {
            console.error('Error fetching reviews', error);
        }
    }, [axiosFetch]);

    useEffect(() => {
        fetchTenantAsync();
    }, [fetchTenantAsync]);

    return {
        tenant,
        isGithugConnected: !!tenant?.github_installation_id,
        startGithubConnect
    };
};

// Create the context
const OrgSettingsContext = createContext<OrgSettingsModel | undefined>(undefined);

// Create the provider component
const OrgSettingsProvider: React.FC<any> = ({ children }) => {
    const value = useOrgSettingsModel();

    return (
        <OrgSettingsContext.Provider value={value}>
            {children}
        </OrgSettingsContext.Provider>
    );
};

export { OrgSettingsContext, OrgSettingsProvider };