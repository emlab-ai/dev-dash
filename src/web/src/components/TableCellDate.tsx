import { VStack, Text} from "@chakra-ui/react"

export const TableCellDate = ({date}:any) => {
    return (
        <VStack align="flex-start" spacing={0}>
            <Text fontSize="xs">{new Date(date).toLocaleDateString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '/')}</Text>
            <Text fontSize="2xs">{new Date(date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</Text>
        </VStack>
    )
}