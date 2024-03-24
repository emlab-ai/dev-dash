import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import Layout from '@src/pages/layouts/Layout'
import Dashboard from '@src/pages/dashboard/Dashboard'
import SettingsPage from '@src/pages/settings/SettingsPage'
import PullRequestsPage from '@src/pages/pullRequests/page'
import { PullRequestsProvider } from '@src/providers/pullRequestsViewModel'
import { UserDataProvider } from '@src/providers/orgProvider'
import { DashboardProvider } from '@src/providers/dashboardViewModel'
import { UsersStatsProvider } from '@src/providers/usersStatsViewModel'
import UsersStatsPage from '@src/pages/userStats/page'
import TeamsSettings from '@src/pages/settings/teams/TeamsSettings'
import UsersSettings from '@src/pages/settings/users/UsersSettings'
import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react';
import UnauthenticatedLayout from '@src/pages/layouts/UnauthenticatedLayout'
import { Box, Text } from '@chakra-ui/react'


export default function Router () {
    return <BrowserRouter>
        <AuthenticatedTemplate>
            <UserDataProvider>
                <Routes>
                    <Route path="/" element={<Layout />}>
                            <Route index element={<DashboardProvider><Dashboard /></DashboardProvider>} />
                            <Route path="pullrequests" element={<PullRequestsProvider><PullRequestsPage /></PullRequestsProvider>} />
                            <Route path="usersstats/:id?" element={<UsersStatsProvider><UsersStatsPage /></UsersStatsProvider>} />
                            <Route path="settings" element={ <SettingsPage />}>
                                <Route index element={<Navigate replace to="/settings/teams" />} />
                                <Route path="teams" element={<TeamsSettings />} />
                                <Route path="users" element={<UsersSettings />} />
                            </Route>         
                    </Route>       
                </Routes>           
            </UserDataProvider>
        </AuthenticatedTemplate>
        <UnauthenticatedTemplate>
            <Routes>
                <Route path="/" element={<UnauthenticatedLayout />}>
                        <Route path="login" element={<LoginPage />} />
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