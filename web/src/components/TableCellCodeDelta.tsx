import { Box, Text, HStack, VStack, useColorModeValue } from "@chakra-ui/react";

export const TableCellCodeDelta = ({deletions, additions}: {deletions: number, additions: number}) => {
    const changes = additions + deletions;
    const bred = changes > 100;
    return (
        <Box w="100%" pl={2} pr={2} bg={bred?useColorModeValue('red.100', 'red.100'):undefined} color={bred?useColorModeValue('black', 'black'):undefined}>
            <VStack p={1} spacing={0} alignItems="flex-start">
                <Text fontSize="xs"><Text as="span" fontWeight="bold">{changes}</Text>&nbsp;edits</Text>
                <HStack spacing={1}>
                    <Text color={useColorModeValue('green.400', bred?'green.800':'green.400')} fontSize="2xs" fontWeight="bold">+{additions}</Text>
                    <Text color={useColorModeValue('red.800', bred?'red.800':'red.400')} fontSize="2xs" fontWeight="bold">-{deletions}</Text>
                </HStack>
            </VStack>
        </Box>
    )
}
