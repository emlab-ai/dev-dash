import { Button, Drawer, DrawerOverlay, DrawerContent, DrawerHeader, DrawerCloseButton, DrawerBody, DrawerFooter, FormLabel, FormControl, Flex, HStack, Box, Input, ListItem, List, Textarea, Switch, FormHelperText, useColorModeValue } from "@chakra-ui/react";
import { FC, useCallback, useEffect, useState } from "react";
import { GithubRepo, RepositorySettings } from "@src/model";
import { useAxiosClient } from "@src/clients/backendClient";
import { useForm } from "react-hook-form";
import { useCombobox } from 'downshift';

interface RepositoryEditDrawerProps {
    isOpen: boolean;
    onClose(repo?: RepositorySettings): void;
    onDelete(repo?: RepositorySettings): void;
    mode: "Create" | "Edit",
    value?: RepositorySettings;
}
const initialState = {
};

interface RepositorySelectProps {
    value?: string;
    label?: string;
    onChange?: (value: string) => void;
}

const RepositorySelect: FC<RepositorySelectProps> = ({ label, onChange }) => {
    const [items, setItems] = useState<{ label: string, value: string }[]>([]);
    const [loading, setLoading] = useState(false);
    const axiosFetch = useAxiosClient();

    const loadOptions = useCallback(async (inputValue: string) => {
        setLoading(true);
        const response = await axiosFetch(`/api/git/repos?page_size=100&filter=${inputValue}`);
        const result = await response.data;
        const data = result.data.map((item: GithubRepo) => ({ label: item.name, value: item.id }));
        setItems(data);
        setLoading(false);
    }, [axiosFetch]);

    const {
        isOpen,
        getMenuProps,
        getInputProps,
        getItemProps,
        setInputValue
    } = useCombobox<{ label: string, value: string }>({
        items,
        onSelectedItemChange: ({ selectedItem }) => {
            onChange?.(selectedItem.value); // Update the selected item
        },
        onInputValueChange: ({ inputValue }) => loadOptions(inputValue),
        itemToString: (item) => (item ? item.label : ''),
    });

    useEffect(() => {
        setInputValue(label || '');
    }, [label, setInputValue]);

    const backgroundColor = useColorModeValue("white", "gray.800");
    const hoverColor = useColorModeValue('gray.100', 'gray.700');

    return <Box position="relative">
        <Input {...getInputProps()} placeholder="Type to search..." />
        <List {...getMenuProps()}
            border="1px solid"
            borderColor="gray.300"
            borderRadius="md"
            position={"absolute"}
            boxShadow="md"
            bg={backgroundColor}
            display={(!loading && isOpen && items && items.length > 0) ? 'block' : 'none'}
            py={4}
            maxHeight="200px"
            overflowY="auto"
            zIndex={100}
            width="100%">
            {
                items.map((item, index) => (
                    <ListItem
                        px={4}
                        py={2}
                        key={item.value}
                        {...getItemProps({ item, index })}
                        cursor={"pointer"}
                        _hover={{bg: hoverColor}}
                    >
                        {item.label}
                    </ListItem>
                ))
            }
            {loading && <ListItem>Loading...</ListItem>}
        </List>        
    </Box>
}


export default function RepositoryEditDrawer({ isOpen, onClose, onDelete, mode, value }: RepositoryEditDrawerProps) {
    const {
        handleSubmit,
        watch,
        setValue,
        register,
        reset
    } = useForm<RepositorySettings>({
        defaultValues: value || initialState,
        mode: 'onBlur'
    });
    
    useEffect(() => {
        reset(value);
    }, [reset, value]);

    const formData = watch();

    const handleRepoChange = useCallback((value: string ) => {
        setValue('repositoryId', value);
    }, [setValue]);

    const onSubmit = useCallback((data: RepositorySettings) => {
        onClose(data);
    }, [onClose]);

    return (
        <Drawer isOpen={isOpen} onClose={() => onClose()} size={"xl"}>
            <DrawerOverlay />
            <DrawerContent>
                <DrawerHeader>{mode === "Create" ? 'Add new settings' : 'Edit the setting'}</DrawerHeader>
                <DrawerCloseButton />
                <DrawerBody height="100%">
                    <form onSubmit={handleSubmit(onSubmit)} style={{ height: "100%" }}>
                        <FormControl mt={4}>
                            <FormLabel>Repository</FormLabel>
                            <RepositorySelect value={formData.repositoryId} label={formData.name} onChange={handleRepoChange} />                            
                        </FormControl>

                        <FormControl mt={4}>
                            <FormLabel>Disable tracking</FormLabel>
                            <Switch {...register("disableTracking")}/>
                            <FormHelperText>If checked, disables repository to affect users stats.</FormHelperText>
                        </FormControl>

                        <FormControl mt={4}>
                            <FormLabel>Description</FormLabel>
                            <Textarea {...register("description")} height="120px"/>
                        </FormControl>

                        <FormControl mt={4}>
                            <FormLabel>Enable AI description review</FormLabel>
                            <Switch {...register("enableDescriptionReview")}/>
                            <FormHelperText>If checked, enables PR description review.</FormHelperText>
                        </FormControl>

                        <FormControl mt={4}>
                            <FormLabel>Review Prompt</FormLabel>
                            <Textarea {...register("reviewPrompt")} height="200px"/>
                        </FormControl>
                    </form>
                </DrawerBody>
                <DrawerFooter>
                    <Flex flex={1} w="100%" justifyContent="space-between">
                        {mode === 'Edit' && <Button colorScheme="red" variant="ghost" onClick={() => onDelete(value)} justifySelf={"flex-start"}>Delete</Button>}
                        {mode === 'Create' && <Box />}
                        <HStack justifySelf="flex-end">
                            <Button colorScheme="gray" variant="ghost" onClick={() => onClose()}>Cancel</Button>
                            <Button colorScheme="green" mr={3} onClick={handleSubmit(onSubmit)}>{mode === 'Create' ? 'Add' : 'Update'}</Button>
                        </HStack>
                    </Flex>
                </DrawerFooter>

            </DrawerContent>
        </Drawer>
    );
}
