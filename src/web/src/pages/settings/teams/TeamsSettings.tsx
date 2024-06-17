import { TableContainer, Table, Thead, Tr, Th, Tbody, Td, Box, Button, useDisclosure, useColorModeValue } from "@chakra-ui/react";
import { AddIcon } from "@chakra-ui/icons";
import { TeamsSettingsProvider, useTeamsSettingsContext } from "./TeamsSettingsProvider";
import Pager from "@src/components/Pager";
import TeamEditModal from "./TeamEditModal";
import { useCallback, useState } from "react";
import { Team } from "@src/model";

function TeamsSettings() {
    const hoverColor = useColorModeValue("blackAlpha.100", "whiteAlpha.100");
    const {isOpen, onOpen, onClose} = useDisclosure();
    const {teams, nextPage, prevPage, hasNext, hasPrev, createTeamAsync, updateTeamAsync, deleteTeamAsync} = useTeamsSettingsContext();
    const [mode, setMode] = useState<"Create" | "Edit">("Create");
    const [team, setTeam] = useState<Team | undefined>();

    const onComplete = useCallback(async (result: any)=>{
        if(!result) {
            onClose();
            return;            
        }

        if (mode === "Create") {
            await createTeamAsync(result);
        } else {
            await updateTeamAsync(result);
        }

        onClose();
    }, [mode]);

    const onDelete = useCallback(async (result: Team)=>{
        if(!result || !result.id) {
            onClose();
            return;            
        }

        if (confirm('Are you sure you want to delete this team?') === false) {
            return;            
        }

        await deleteTeamAsync(result.id);

        onClose();
    }, []);

    const onAddNew = useCallback(()=>{
        setMode("Create");
        setTeam(undefined);
        onOpen();
    }, []);

    const onEdit = useCallback((team:Team)=>{
        setMode("Edit");
        setTeam(team);
        onOpen();
    }, []);

    return (
        <>
        <Box display="flex" flexDirection="column" position="absolute" m={0} top={0} left={0} right={0} bottom={0} overflow="hidden">
            <Box justifyContent="flex-end" p={4} display="flex">
                <Button leftIcon={<AddIcon />} colorScheme="teal" onClick={onAddNew}>Add team</Button>
            </Box>
            <Box flex={1} m={0} overflow="scroll" width="100%" height="100%">
                <TableContainer >
                    <Table variant='simple'>
                        <Thead>
                        <Tr>
                            <Th>Name</Th>
                            <Th>Parent Team</Th>
                        </Tr>
                        </Thead>
                        <Tbody>
                            {teams && teams.map(team=>(
                                <Tr key={team.id} onClick={()=>onEdit(team)} _hover={{ bg: hoverColor, cursor: "pointer" }}>
                                    <Td>{team.name}</Td>
                                    <Td>{team.parentName}</Td>
                                </Tr>
                            ))}
                    
                        </Tbody>
                    </Table>                
                </TableContainer>
                <Pager nextPage={nextPage} prevPage={prevPage} hasNext={hasNext} hasPrev={hasPrev}/>
            </Box>
        </Box>
        <TeamEditModal isOpen={isOpen} onClose={onComplete} onDelete={onDelete} mode={mode} value={team}/>
        </>
    );
}

export default function TeamsSettingsWithData() {
    return <TeamsSettingsProvider>
        <TeamsSettings/>
    </TeamsSettingsProvider>
}