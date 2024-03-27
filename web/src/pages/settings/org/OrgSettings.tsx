import { Box, Button } from "@chakra-ui/react";
import { FaGithub } from "react-icons/fa";
import { OrgSettingsProvider, useOrgSettingsModel } from "./OrgSettingsProvider";


function OrgSettings() {

    const { isGithugConnected, startGithubConnect } = useOrgSettingsModel();
 
    return (
        <>
        <Box>
            {!isGithugConnected && <Button leftIcon={<FaGithub />} colorScheme="teal" onClick={startGithubConnect}>Connect GitHub</Button>}
        </Box>
        </>
    );
}

export default function TeamsSettingsWithData() {
    return <OrgSettingsProvider>
        <OrgSettings/>
    </OrgSettingsProvider>
}