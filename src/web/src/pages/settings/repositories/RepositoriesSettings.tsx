import { TableContainer, Table, Thead, Tr, Th, Tbody, Td, Box, Button, useDisclosure, useColorModeValue } from "@chakra-ui/react";
import { AddIcon } from "@chakra-ui/icons";
import { RepoSettingsProvider, useRepoSettingsContext } from "./RepositoriessSettingsProvider";
import Pager from "@src/components/Pager";
import { useCallback, useState } from "react";
import { RepositorySettings } from "@src/model";
import RepositoryEditDrawer from "./RepositoryEditDrawer";

function RepositoriesSettings() {
    const hoverColor = useColorModeValue("blackAlpha.100", "whiteAlpha.100");
    const {isOpen, onOpen, onClose} = useDisclosure();
    const {repoSettings, nextPage, prevPage, hasNext, hasPrev, createRepoSettingsAsync, deleteRepoSettingsAsync, updateRepoSettingsAsync} = useRepoSettingsContext();
    const [mode, setMode] = useState<"Create" | "Edit">("Create");
    const [repo, setRepo] = useState<RepositorySettings | undefined>();

    const onComplete = useCallback(async (result: any)=>{
        if(!result) {
            onClose();
            return;            
        }

        if (mode === "Create") {
            await createRepoSettingsAsync(result);
        } else {
            await updateRepoSettingsAsync(result);
        }

        onClose();
    }, [mode, onClose, createRepoSettingsAsync, updateRepoSettingsAsync]);

    const onDelete = useCallback(async (result: RepositorySettings)=>{
        if(!result || !result.id) {
            onClose();
            return;            
        }

        if (confirm('Are you sure you want to delete the repository settings?') === false) {
            return;            
        }

        await deleteRepoSettingsAsync(result.id);

        onClose();
    }, [deleteRepoSettingsAsync, onClose]);

    const onAddNew = useCallback(()=>{
        setMode("Create");
        setRepo(undefined);
        onOpen();
    }, [setMode, setRepo, onOpen]);

    const onEdit = useCallback((repo:RepositorySettings)=>{
        setMode("Edit");
        setRepo(repo);
        onOpen();
    }, [setMode, setRepo, onOpen]);

    return (
        <>
        <Box display="flex" flexDirection="column" position="absolute" m={0} top={0} left={0} right={0} bottom={0} overflow="hidden">
            <Box justifyContent="flex-end" p={4} display="flex">
                <Button leftIcon={<AddIcon />} colorScheme="teal" onClick={onAddNew}>Add repository settings</Button>
            </Box>
            <Box flex={1} m={0} overflow="scroll" width="100%" height="100%">
                <TableContainer >
                    <Table variant='simple'>
                        <Thead>
                        <Tr>
                            <Th>Name</Th>
                        </Tr>
                        </Thead>
                        <Tbody>
                            {repoSettings && repoSettings.map(repo=>(
                                <Tr key={repo.id} onClick={()=>onEdit(repo)} _hover={{ bg: hoverColor, cursor: "pointer" }}>
                                    <Td>{repo.name}</Td>
                                </Tr>
                            ))}
                        </Tbody>
                    </Table>                
                </TableContainer>
                <Pager nextPage={nextPage} prevPage={prevPage} hasNext={hasNext} hasPrev={hasPrev}/>
            </Box>
        </Box>
        <RepositoryEditDrawer isOpen={isOpen} onClose={onComplete} onDelete={onDelete} mode={mode} value={repo}/>
        </>
    );
}

export default function RepositorySettingsWithData() {
    return <RepoSettingsProvider>
        <RepositoriesSettings/>
    </RepoSettingsProvider>
}