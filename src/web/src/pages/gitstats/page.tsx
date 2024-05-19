import { Container, Flex, Tabs, TabList, Tab, TabPanels } from "@chakra-ui/react";
import ScopeFilter from "@src/components/ScopeFilter";
import { useGitStatsContext } from "@src/providers/gitStatsViewModel";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

export default function GitStatsPage() {

    const {timeFilter, setTimeFilter, managerFilter, setManagerFilter} = useGitStatsContext();

    const navigate = useNavigate();
    const location = useLocation();
    let currentTab = 0;
    if (location.pathname.indexOf("pullrequests") > 0) {
        currentTab = 0;
    } else if (location.pathname.indexOf("users") > 0) {
        currentTab = 1;
    } else if (location.pathname.indexOf("repositories") > 0) {
        currentTab = 2;
    }

    const handleTabsChange = (index: number) => {
        switch (index) {
            case 0:
                navigate("/gitstats/pullrequests");
                break;
            case 1:
                navigate("/gitstats/users");
                break;
            case 2:
                navigate("/gitstats/repositories");
                break;
            default:
                break;
        }
    };

    return (
        <Flex flexDir="column" w="100%" h="100%" pl={4} pr={4}>
            <ScopeFilter managerFilter={managerFilter} timeFilter={timeFilter} setTimeFilter={setTimeFilter} setManagerFilter={setManagerFilter} />
            <Tabs index={currentTab} onChange={handleTabsChange}>
                <TabList>
                    <Tab>Pull requests</Tab>
                    <Tab>Users</Tab>
                    <Tab>Repositories</Tab>
                </TabList>
                <TabPanels>
                </TabPanels>
            </Tabs>
            <Container w="100%" maxW="full" flex={1} position="relative" >
                <Outlet />
            </Container>

        </Flex>
    )
}