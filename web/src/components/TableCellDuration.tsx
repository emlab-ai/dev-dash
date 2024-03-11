import { Text} from "@chakra-ui/react";

export const TableCellDuration = ({hours}: {hours:number}) => { 
    if (hours >= 24) { 
        const days = Math.floor(hours / 24); 
        const remainingHours = hours % 24; 
        return <Text><Text as="span" fontWeight="semibold">{days}</Text> d <Text as="span" fontWeight="semibold">{Math.floor(remainingHours)}</Text> h</Text>; 
    } else { 
        const minutes = hours * 60; 
        const remainingMinutes = minutes % 60; 
        return <Text><Text as="span" fontWeight="semibold">{Math.floor(minutes / 60)}</Text> h <Text as="span" fontWeight="semibold">{Math.floor(remainingMinutes)}</Text> m</Text>; 
    } 
};