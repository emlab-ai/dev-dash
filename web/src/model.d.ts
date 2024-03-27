export interface Team {
    id?:string;
    name: string;
    parentName?: string;
    parentId?: string;
    gitHubTeamId?: string;
    members?: TeamMember[];
    tags?: string[];
}

export interface TeamMember {
    userId: string;
    teamId: string;
}

export interface User {
    id?:string;
    name: string;
    gitHubUserId?: string;
    tags?: string;
    gitAlias?: string;
    managerId?: string;
    managerName?: string;
    isManager?: boolean;
    level?: string;
    email?: string;
    teamId?: string;
    teamName?: string;
}

export interface PagedResult<Data extends object> {
    data: Data[];
    before: string | null;
    after: string | null;
    total_count: number;
}

export interface Tenant {
    id: string;
    name: string;    
    oauth_tenant_id: string
    organization_domain: string
    github_installation_id: number;
    github_installation_token:string
}