import { Box, HStack, Text } from "@chakra-ui/react"
import { useCallback } from 'react';
import DateFilterToggle from "./DateFilterToggle";
import UserSelect from "./UserSelect";


type ScopeFilterProps = {
  timeFilter: string;
  setTimeFilter: (timeFilter: string) => void;
  managerFilter: string;
  setManagerFilter: (managerFilter: string) => void;
}

export default function ScopeFilter({ timeFilter, setTimeFilter, managerFilter, setManagerFilter }: ScopeFilterProps) {
  const handleDateChange = useCallback((newValue:any) => {
    setTimeFilter(newValue);
  }, [setTimeFilter]);

  return <HStack justify="space-between" px="4">
    <Box p={4}>
      <HStack>
        <Text>Timeframe:</Text>
        <DateFilterToggle value={timeFilter} onChange={handleDateChange} size="sm"/>
      </HStack>
    </Box>
    <Box>
      <HStack>
        <Text>Manager:</Text>
        <UserSelect size="sm" w="200px" isManager value={managerFilter} onChange={(e:any) => setManagerFilter(e.target.value)}/>        
      </HStack>
    </Box>
  </HStack>
}