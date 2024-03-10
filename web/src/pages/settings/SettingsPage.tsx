import { Box, Tab, TabList, TabPanel,  TabPanels, Tabs } from "@chakra-ui/react";
import TribesSettings from "./TribesSettings"; // Import the TribesSetting component

function SettingsPage() {
    return (
        <Box p={4}>
        <Tabs>
                <TabList>
                    <Tab>Users</Tab>
                    <Tab>Teams</Tab>
                    <Tab>Trbes</Tab>
                </TabList>

                <TabPanels>
                    <TabPanel>
                        <Form/>
                    </TabPanel>
                    <TabPanel>
                        <Form/>
                    </TabPanel>
                    <TabPanel>
                        <TribesSettings /> 
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Box>
    );
}


function Form() {
    // Implement your form component here
    return <Box>Form Component</Box>;
}

export default SettingsPage;