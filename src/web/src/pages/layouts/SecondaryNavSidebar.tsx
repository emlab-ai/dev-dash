import { Box, HStack, List, Flex, useColorModeValue, Text, ListItem, ListIcon } from "@chakra-ui/react";
import { Link, Outlet, useLocation } from "react-router-dom";

interface SecondaryNavSidebarPropsItem {
    text: string;
    url: string;
    icon?: any;
}

interface SecondaryNavSidebarProps {
    items: SecondaryNavSidebarPropsItem[];
}

function SecondaryNavSidebar({ items }: SecondaryNavSidebarProps) {
    const location = useLocation();
    const currentPath = location.pathname;
    return (
        <HStack spacing={2} p={4} align="flex-start" h="100%">
            <Box minW="180px" as="aside" minH="90vh" borderColor={useColorModeValue('gray.50', 'gray.900')} transition="width 0.25s ease">
                <Text fontSize="xl" fontWeight="bold">Settings</Text>
                <List spacing={0} p="0.5" pt={2}>
                    {
                        items.map(item => (<ListElement key={item.url} text={item.text} url={item.url} selected={item.url === currentPath} />))
                    }
                </List>
            </Box>
            <Flex w='full' m={0} h="100%">
                <Box w="100%" position="relative" m={0} h="100%" justifyItems="stretch">
                    <Outlet />
                </Box>
            </Flex>
        </HStack>
    );
}

const ListElement = ({ text, url, selected, icon }: { text: string, url: string, selected: boolean, icon?: any }) => {
    const hoverColor = useColorModeValue('gray.100', 'gray.700');
    const selectedColor = useColorModeValue('gray.200', 'gray.500');

    return (
        <Link to={url}>
            <ListItem as={HStack} spacing={0} h="10" pl="2.5" cursor="pointer" _hover={{ bg: hoverColor }} rounded="md" background={selected ? selectedColor : undefined}>
                {icon && <ListIcon boxSize={5} as={icon} />}
                {
                    text && <Text>{text}</Text>
                }
            </ListItem>
        </Link>
    );
}


export default SecondaryNavSidebar;