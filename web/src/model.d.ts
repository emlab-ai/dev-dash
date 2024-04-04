import exp from "constants";

export interface Team {
    id?:number;
    name: string;
    parentName?: string;
    parentId?: number;
    gitHubTeamId?: number;
    members?: TeamMember[];
    tags?: string[];
}

export interface TeamMember {
    userId: number;
    teamId: number;
}

export interface User {
    id?:number;
    name: string;
    githubUserId?: number;
    tags?: string;
    gitAlias?: string;
    managerId?: number;
    managerName?: string;
    isManager?: boolean;
    level?: string;
    email?: string;
    teamId?: number;
    teamName?: string;
}

export interface PagedResult<Data extends object> {
    data: Data[];
    before: string | null;
    after: string | null;
    totalCount: number;
}

export interface GithubOrg {
    id: number;
    name: string;
    installationId: number;
}

export interface Tenant {
    id: number;
    name: string;    
    oauthTenantId: string
    organizationDomain: string
    githubOrgs: GithubOrg[];
}