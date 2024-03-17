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