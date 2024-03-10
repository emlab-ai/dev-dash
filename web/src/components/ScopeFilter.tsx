import { Box, HStack, Select, Text } from "@chakra-ui/react"
import { useUsersProviderContext } from "@src/providers/usersProvider";

type ScopeFilterProps = {
    timeFilter: string;
    setTimeFilter: (timeFilter: string) => void;
    managerFilter: number;
    setManagerFilter: (managerFilter: number) => void;
}

export default function ScopeFilter({timeFilter, setTimeFilter, managerFilter, setManagerFilter}:ScopeFilterProps) {
    const { managers } = useUsersProviderContext();
    
    return <HStack justify="space-between" px="4">
    <Box p={4}>
      <HStack>
        <Text>Timeframe:</Text>
        <Select w="100%" defaultValue={timeFilter} onChange={(e)=>{setTimeFilter(e.target.value)}}>
          <option value="1month">Last month</option>
          <option value="6months">Last 6 months</option>
          <option value="12months">Last 12 months</option>
          {/* <option value="custom">Custom</option> */}
        </Select>
      </HStack>
    </Box>
    <Box>
      <HStack>
        <Text>Manager:</Text>
        <Select w="100%" defaultValue={managerFilter} onChange={(e) => setManagerFilter(Number.parseInt(e.target.value))}>
          {managers.map((manager) => <option key={manager.id} value={manager.id}>{manager.name}</option>)}
        </Select>
      </HStack>
    </Box>
  </HStack>
}