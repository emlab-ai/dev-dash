import { TableContainer, Text, Table, useColorModeValue, Thead, Tr, Th, Tbody, Td, Box, Button, Avatar, useDisclosure } from "@chakra-ui/react";
import { AddIcon } from "@chakra-ui/icons";
import { UsersSettingsProvider, useUsersSettingsContext } from "./UsersSettingsProvider";
import Pager from "@src/components/Pager";
import { User } from "@src/model";
import { useCallback, useState } from "react";
import UserEditModal from "./UserEditModal";

function UsersSettings() {
    const hoverColor = useColorModeValue("blackAlpha.100", "whiteAlpha.100");
    const {refreshAsync, users, nextPage, prevPage, hasNext, hasPrev, createUserAsync, updateUserAsync, deleteUserAsync} = useUsersSettingsContext();

    const {isOpen, onOpen, onClose} = useDisclosure();
    const [mode, setMode] = useState<"Create" | "Edit">("Create");
    const [user, setUser] = useState<User | undefined>();

    const onComplete = useCallback(async (result: any)=>{
        if(!result) {
            onClose();
            return;            
        }
        if (mode === "Create") {
            await createUserAsync(result);
        } else {
            await updateUserAsync(result);
        }
        await refreshAsync();
        onClose();
    }, [mode, onClose]);

    const onDelete = useCallback(async (result: User)=>{
        if(!result || !result.id) {
            onClose();
            return;            
        }

        if (confirm('Are you sure you want to delete this team?') === false) {
            return;            
        }

        await deleteUserAsync(result.id);

        onClose();
    }, [onClose]);

    const onAddNew = useCallback(()=>{
        setMode("Create");
        setUser(undefined);
        onOpen();
    }, [onOpen]);

    const onEdit = useCallback((user:User)=>{
        setMode("Edit");
        setUser(user);
        onOpen();
    }, [onOpen]);

        
    return (
        <>
        <Box>
            <Box justifyContent="flex-end" p={4} display="flex">
                <Button leftIcon={<AddIcon />} colorScheme="teal" onClick={onAddNew}>Add user</Button>
            </Box>
            <TableContainer>
                <Table variant='simple'>
                    <Thead>
                        <Tr>
                            <Th></Th>
                            <Th>Name</Th>
                            <Th>Manager</Th>
                            <Th>Team</Th>
                            <Th>GitAlias</Th>                            
                            <Th>Email</Th>
                        </Tr>
                    </Thead>
                    <Tbody>
                        {users && users.map((user:User) => (
                        <Tr key={user.id} onClick={()=>onEdit(user)}  _hover={{ bg: hoverColor, cursor: "pointer" }}>
                            <Td><Avatar name={user.name} size='sm'/></Td>                            
                            <Td>{user.name}</Td>
                            <Td>{user.managerName}</Td>
                            <Td>{user.teamName}</Td>
                            <Td>{user.gitAlias}</Td>
                            <Td>{user.email}</Td>
                        </Tr>
                        ))}
                    </Tbody>
                    
                </Table>
            </TableContainer>

            <Pager nextPage={nextPage} prevPage={prevPage} hasNext={hasNext} hasPrev={hasPrev} />
        </Box>
        <UserEditModal isOpen={isOpen} onClose={onComplete} onDelete={onDelete} mode={mode} value={user}/> 
        </>
    );
}

export default function UsersSettingsWithData() {
    return <UsersSettingsProvider><UsersSettings/></UsersSettingsProvider>
}