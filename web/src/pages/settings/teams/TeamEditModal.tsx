import { Button, Drawer, DrawerOverlay, DrawerContent, DrawerHeader, DrawerCloseButton, DrawerBody, DrawerFooter, FormLabel, Input, Select, FormControl, FormHelperText, Flex, HStack, Box } from "@chakra-ui/react";
import { useTeamsSettingsContext } from "./TeamsSettingsProvider";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Team } from "@src/model";

interface TeamEditDrawerProps {
    isOpen:boolean;
    onClose(team?:Team):void;
    onDelete(team?:Team):void;
    mode: "Create" | "Edit",
    value?:Team;
}
const initialState = {
    name: ""
};

export default function TeamEditDrawer({isOpen, onClose, onDelete, mode, value}:TeamEditDrawerProps) {
    const {teams} = useTeamsSettingsContext();

    const [formData, setFormData] = useState<Team>(initialState);
    useEffect(()=>{
        if(value)
            setFormData(value);
        else 
            setFormData(initialState);
    }, [value, setFormData, initialState]);

    const handleChange = useCallback((e:any) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
          ...prev,
          [name]: value,
        }));
      }, [setFormData]);
    
      const handleSubmit = useCallback((e:any) => {
        e.preventDefault();
        onClose(formData); 
      }, [formData, onClose]);

    const filteredTeams = useMemo(()=>teams?.filter(t=>t.id !== value?.id), [teams, value]);

    return (
        <Drawer isOpen={isOpen} onClose={()=>onClose()}>
            <DrawerOverlay/>
            <DrawerContent>
                <form onSubmit={handleSubmit}>
                <DrawerHeader>{mode === "Create" ? 'Add new team': 'Edit the team'}</DrawerHeader>
                <DrawerCloseButton />
                <DrawerBody>
                    <FormControl>
                        <FormLabel>Name</FormLabel>
                        <Input isRequired type="name" name="name" value={formData.name} onChange={handleChange}></Input>
                    </FormControl>
                    <FormControl mt={4}>
                        <FormLabel>Parent Team</FormLabel>
                        <Select name="parentId" placeholder="Select a team" value={formData?.parentId ?? ""} onChange={handleChange}>     
                            {filteredTeams && filteredTeams.map(t=>(<option key={t.id} value={t.id}>{t.name}</option>))}
                        </Select>
                        <FormHelperText fontSize="xs" pl={2}>optional</FormHelperText>
                    </FormControl>                    
                </DrawerBody>
                <DrawerFooter>
                    <Flex flex={1} w="100%" justifyContent="space-between">
                        {mode==='Edit' && <Button colorScheme="red" variant="ghost" onClick={()=>onDelete(value)} justifySelf={"flex-start"}>Delete</Button>}
                        {mode==='Create' && <Box/>}
                        <HStack justifySelf="flex-end">
                            <Button colorScheme="gray" variant="ghost" onClick={()=>onClose()}>Cancel</Button>
                            <Button colorScheme="green" mr={3} type="submit">{mode === 'Create'?'Add': 'Update'}</Button>
                        </HStack>
                    </Flex>
                </DrawerFooter>
                </form>
            </DrawerContent>
        </Drawer>
    );
}
