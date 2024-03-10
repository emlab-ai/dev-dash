import { BrowserRouter, Route, Routes } from 'react-router-dom'

import Layout from '@src/pages/layouts/Layout'
import Dashboard from '@src/pages/dashboard/Dashboard'
import SettingsPage from '@src/pages/settings/SettingsPage'
import PullRequestsPage from '@src/pages/pullRequests/page'
import { PullRequestsProvider } from '@src/providers/pullRequestsViewModel'
import { QueryClient, QueryClientProvider } from 'react-query'
import { UserDataProvider } from '@src/providers/usersProvider'
import { DashboardProvider } from '@src/providers/dashboardViewModel'
import { UsersStatsProvider } from '@src/providers/usersStatsViewModel'
import UsersStatsPage from '@src/pages/userStats/page'

const queryClient = new QueryClient();

export default function Router () {
    return <BrowserRouter>
    <QueryClientProvider client={queryClient}>
        <UserDataProvider>
            <Routes>
            <Route path="/" element={<Layout />}>
                {/* Index route for the default content */}
                <Route index element={<DashboardProvider><Dashboard /></DashboardProvider>} />
                <Route path="pullrequests" element={<PullRequestsProvider><PullRequestsPage /></PullRequestsProvider>} />
                <Route path="usersstats/:id?" element={<UsersStatsProvider><UsersStatsPage /></UsersStatsProvider>} />
                <Route path="settings" element={ <SettingsPage />} />
            </Route>
            </Routes>
        </UserDataProvider>
    </QueryClientProvider>
  </BrowserRouter>
}
