import { Box, Button, Link, Table, TableContainer, Tbody, Td, Text, Th, Thead, Tr } from "@chakra-ui/react";
import { FaGithub } from "react-icons/fa";
import { OrgSettingsProvider, useOrgSettingsModel } from "./OrgSettingsProvider";


function OrgSettings() {

    const { startGithubConnect, startGithubSync, tenant } = useOrgSettingsModel();
 
    return (
        <>
        <Box>
            <Text>Organisation Settings</Text>
            <TableContainer>
                <Table>
                    <Thead>
                        <Tr>
                            <Th>Name</Th>
                            <Th>Installation ID</Th>  
                            <Th></Th>
                        </Tr>
                    </Thead>
                    <Tbody>
                        {tenant?.githubOrgs?.map(org => (
                            <Tr key={org.id}>
                                <Td>{org.name}</Td>
                                <Td>{org.installationId}</Td>
                                <Td><Link onClick={()=>startGithubSync(org.installationId)}>re-sync</Link></Td>
                            </Tr>
                        ))}
                    </Tbody>
                    </Table>
            </TableContainer>
            {<Button leftIcon={<FaGithub />} colorScheme="teal" onClick={startGithubConnect}>Connect GitHub</Button>}
        </Box>
        </>
    );
}

export default function TeamsSettingsWithData() {
    return <OrgSettingsProvider>
        <OrgSettings/>
    </OrgSettingsProvider>
}