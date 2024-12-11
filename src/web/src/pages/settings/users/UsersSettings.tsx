import { TableContainer, Table, useColorModeValue, Thead, Tr, Th, Tbody, Td, Box, Button, Avatar, useDisclosure, Flex, Input, InputGroup, InputLeftElement } from "@chakra-ui/react";
import { AddIcon, Search2Icon } from "@chakra-ui/icons";
import { UsersSettingsProvider, useUsersSettingsContext } from "./UsersSettingsProvider";
import Pager from "@src/components/Pager";
import { User } from "@src/model";
import { useCallback, useState } from "react";
import UserEditModal from "./UserEditModal";

function UsersSettings() {
    const hoverColor = useColorModeValue("blackAlpha.100", "whiteAlpha.100");
    const { userFilter, setUserFilter, refreshAsync, users, nextPage, prevPage, hasNext, hasPrev, createUserAsync, updateUserAsync, deleteUserAsync } = useUsersSettingsContext();

    const { isOpen, onOpen, onClose } = useDisclosure();
    const [mode, setMode] = useState<"Create" | "Edit">("Create");
    const [user, setUser] = useState<User | undefined>();

    const onComplete = useCallback(async (result: User) => {
        if (!result) {
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
    }, [mode, onClose, createUserAsync, updateUserAsync, refreshAsync]);

    const onDelete = useCallback(async (result: User) => {
        if (!result || !result.id) {
            onClose();
            return;
        }

        if (confirm('Are you sure you want to delete the user?') === false) {
            return;
        }

        await deleteUserAsync(result.id);

        onClose();
    }, [onClose, deleteUserAsync]);

    const onAddNew = useCallback(() => {
        setMode("Create");
        setUser({ name: "" });
        onOpen();
    }, [onOpen]);

    const onEdit = useCallback((user: User) => {
        setMode("Edit");
        setUser(user);
        onOpen();
    }, [onOpen]);

    return (
        <>
            <Box display="flex" flexDirection="column" position="absolute" m={0} top={0} left={0} right={0} bottom={0} overflow="hidden">
                <Flex p={4} justify="space-between" >
                    <InputGroup>
                        <InputLeftElement pointerEvents="none" children={<Search2Icon color="gray.300" />} />
                        <Input placeholder="Search" width={"24em"} value={userFilter} onChange={e => setUserFilter(e.target.value)} />
                    </InputGroup>
                    <Button leftIcon={<AddIcon />} colorScheme="teal" onClick={onAddNew}>Add user</Button>
                </Flex>
                <Box flex={1} m={0} overflow="scroll" width="100%" height="100%">
                    <TableContainer width="100%">
                        <Table variant='simple' width="100%">
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
                                {users && users.map((user: User) => (
                                    <Tr key={user.id} onClick={() => onEdit(user)} _hover={{ bg: hoverColor, cursor: "pointer" }}>
                                        <Td><Avatar name={user.name} size='sm' /></Td>
                                        <Td>{user.name}</Td>
                                        <Td>{user.manager?.name}</Td>
                                        <Td>{user.team?.name}</Td>
                                        <Td>{user.githubUser?.login}</Td>
                                        <Td>{user.email}</Td>
                                    </Tr>
                                ))}
                            </Tbody>

                        </Table>
                    </TableContainer>
                    <Pager nextPage={nextPage} prevPage={prevPage} hasNext={hasNext} hasPrev={hasPrev} />
                </Box>
            </Box>
            <UserEditModal isOpen={isOpen} onClose={onComplete} onDelete={onDelete} mode={mode} value={user} />
        </>
    );
}

export default function UsersSettingsWithData() {
    return <UsersSettingsProvider><UsersSettings /></UsersSettingsProvider>
}