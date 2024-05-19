import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import Layout from '@src/pages/layouts/Layout'
import Dashboard from '@src/pages/dashboard/Dashboard'
import SettingsPage from '@src/pages/settings/SettingsPage'
import { PullRequestsProvider } from '@src/providers/pullRequestsViewModel'
import { UserDataProvider } from '@src/providers/orgProvider'
import { DashboardProvider } from '@src/providers/dashboardViewModel'
import { UsersStatsProvider } from '@src/providers/usersStatsViewModel'
import TeamsSettings from '@src/pages/settings/teams/TeamsSettings'
import UsersSettings from '@src/pages/settings/users/UsersSettings'
import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react';
import UnauthenticatedLayout from '@src/pages/layouts/UnauthenticatedLayout'
import { Box, Text } from '@chakra-ui/react'
import OrgSettings from '@src/pages/settings/org/OrgSettings'
import SignupPage from '@src/pages/auth/SignupPage'
import GitStatsPage from '@src/pages/gitstats/page'
import UsersStatsPage from '@src/pages/gitstats/userStats/page'
import ReposStatsPage from '@src/pages/gitstats/repoStats/page'
import PullRequestsPage from '@src/pages/gitstats/pullRequests/page'
import { GitStatsProvider } from '@src/providers/gitStatsViewModel'
import { RepoStatsProvider } from '@src/providers/reposStatsViewModel'

export default function Router () {
    return <BrowserRouter>
        <AuthenticatedTemplate>
            <UserDataProvider>
                <Routes>
                    <Route path="/" element={<Layout />}>
                            <Route index element={<DashboardProvider><Dashboard /></DashboardProvider>} />
                            <Route path="gitstats" element={<GitStatsProvider><GitStatsPage /></GitStatsProvider>}>
                                <Route index element={<Navigate replace to="/gitstats/pullrequests" />} />
                                <Route path="pullrequests" element={<PullRequestsProvider><PullRequestsPage /></PullRequestsProvider>} />
                                <Route path="users/:id?" element={<UsersStatsProvider><UsersStatsPage /></UsersStatsProvider>} />
                                <Route path="repositories" element={<RepoStatsProvider><ReposStatsPage/></RepoStatsProvider>} />
                            </Route>
                            <Route path="settings" element={ <SettingsPage />}>
                                <Route index element={<Navigate replace to="/settings/organisation" />} />
                                <Route path="organisation" element={<OrgSettings />} />
                                <Route path="teams" element={<TeamsSettings />} />
                                <Route path="users" element={<UsersSettings />} />
                            </Route>         
                            <Route path="signup" element={<SignupPage />} />
                    </Route>       
                </Routes>           
            </UserDataProvider>
        </AuthenticatedTemplate>
        <UnauthenticatedTemplate>
            <Routes>
                <Route path="/" element={<UnauthenticatedLayout />}>
                    <Route path="login" element={<LoginPage />} />
                    <Route path="signup" element={<SignupPage />} />
                </Route>
            </Routes>
        </UnauthenticatedTemplate>
  </BrowserRouter>
}


const  LoginPage = () => {  
    return <Box>
        <Text>Login</Text>
    </Box>
}