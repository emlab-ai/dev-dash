import { Button, Drawer, DrawerOverlay, DrawerContent, DrawerHeader, DrawerCloseButton, DrawerBody, DrawerFooter, FormLabel, Input, Select, FormControl, FormHelperText, Flex, HStack, Box, Radio, Switch, SimpleGrid, FormErrorMessage } from "@chakra-ui/react";
import { useEffect } from "react";
import { User } from "@src/model";
import { Controller, useForm } from 'react-hook-form';
import TeamSelect from "@src/components/TeamSelect";
import UserSelect from "@src/components/UserSelect";
import { useOrgProviderContext } from "@src/providers/orgProvider";
import TagsSelect from "@src/components/TagsSelect";

interface UserEditDrawerProps {
    isOpen: boolean;
    onClose(user?: User): void;
    onDelete(user?: User): void;
    mode: "Create" | "Edit",
    value?: User;
}
const initialState = {
    name: ""
};

export default function UserEditDrawer({ isOpen, onClose, onDelete, mode, value }: UserEditDrawerProps) {
    const { levels } = useOrgProviderContext();

    const {
        register,
        handleSubmit,
        control,
        reset,
        watch,
        formState: { errors, isSubmitting }
    } = useForm<User>({
        defaultValues: value || initialState,
        mode: 'onBlur'
    });

    useEffect(() => {
        reset(value || initialState);
    }, [value, reset, initialState]);

    const wathchIsManager = watch("isManager");

    return (        
        <Drawer isOpen={isOpen} onClose={() => onClose()} size="md">
            <DrawerOverlay />
            <form onSubmit={handleSubmit(onClose)}>
            <DrawerContent overflowY="auto">
                    <DrawerCloseButton />
                    <DrawerHeader>{mode === "Create" ? 'Add new user' : 'Edit the user'}</DrawerHeader>                
                    <DrawerBody overflowY="auto">
                        <FormControl>
                            <FormLabel>Name</FormLabel>
                            <Input type="text" {...register('name', { required: 'This field is required' })} />
                            <FormErrorMessage>
                                {errors.name && errors.name.message}
                            </FormErrorMessage>
                        </FormControl>
                        <FormControl mt={4}>
                            <FormLabel>Manager</FormLabel>
                            <Controller
                                name="managerId"
                                control={control}
                                render={({ field }) => <UserSelect placeholder="Select a manager" isManager excludeId={value?.id} {...field} />}
                            />
                        </FormControl>
                        <FormControl mt={4}>
                            <FormLabel>Team</FormLabel>
                            <Controller
                                name="teamId"
                                control={control}
                                render={({ field }) => <TeamSelect placeholder="Select a team"  {...field} />}
                            />
                        </FormControl>
                        <FormControl mt={4}>
                            <FormLabel>Git alias</FormLabel>
                            <Input type="text" {...register('gitAlias', { required: false })}></Input>
                        </FormControl>
                        <FormControl mt={4}>
                            <FormLabel>Email</FormLabel>
                            <Input type="email"
                                {...register('email', {
                                    required: false,//'This field is required',
                                    pattern: {
                                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i,
                                        message: 'Invalid email address'
                                    }
                                })}
                            />
                            <FormErrorMessage>
                                {errors.email && errors.email.message}
                            </FormErrorMessage>
                        </FormControl>
                        <FormControl mt={4}>
                            <FormLabel>Is Manager?</FormLabel>
                            <Switch {...register('isManager', { required: false })}></Switch>
                        </FormControl>
                        <FormControl mt={4}>
                            <FormLabel>Level</FormLabel>
                            <Select placeholder="Select a level" {...register('level', { required: true })}>
                                {(wathchIsManager ?
                                    levels.managers :
                                    levels.ics).map((level) => (
                                        <option value={level} key={level}>{level}</option>
                                    ))}
                            </Select>
                        </FormControl>

                        <FormControl mt={4}>
                            <FormLabel>Tags</FormLabel>
                            <Controller
                                name="tags"
                                control={control}
                                render={({ field }) => <TagsSelect placeholder="Select tags"  {...field} />}
                            />
                        </FormControl>
                    </DrawerBody>
                    <DrawerFooter>
                        <Flex flex={1} w="100%" justifyContent="space-between">
                            {mode === 'Edit' && <Button colorScheme="red" variant="ghost" onClick={() => onDelete(value)} justifySelf={"flex-start"}>Delete</Button>}
                            {mode === 'Create' && <Box />}
                            <HStack justifySelf="flex-end">
                                <Button colorScheme="gray" variant="ghost" onClick={() => onClose()}>Cancel</Button>
                                <Button colorScheme="green" mr={3} type="submit" isLoading={isSubmitting} >{mode === 'Create' ? 'Add' : 'Update'}</Button>
                            </HStack>
                        </Flex>
                    </DrawerFooter>
            </DrawerContent>
            </form>
        </Drawer>
        
    );
}
