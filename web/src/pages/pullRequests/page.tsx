import { Box, Divider, Stat, StatLabel, StatNumber, useDisclosure, useColorModeValue, HStack } from '@chakra-ui/react';
import { PullRequest, usePullRequestsContext } from '@src/providers/pullRequestsViewModel';
import { useCallback, useState } from 'react';
import PrDrawer from './components/PrDrawer';
import PrTable from './components/PrTable';
import ScopeFilter from '@src/components/ScopeFilter';

const PullRequestsPage = () => {
    const { isOpen, onOpen, onClose } = useDisclosure()
    const [currentItem, setCurrentItem] = useState<PullRequest | null>(null);

    const onClickOnLine = useCallback((pr: PullRequest) => {
        console.log('clicked on line', pr.id);
        setCurrentItem(pr);
        onOpen();
    }, [onOpen]);

    const {timeFilter, setTimeFilter, managerFilter, setManagerFilter, pullRequestsStats} = usePullRequestsContext();

    return (
        <>
            <Box>
                <ScopeFilter timeFilter={timeFilter} setTimeFilter={setTimeFilter} managerFilter={managerFilter} setManagerFilter={setManagerFilter} />
                {pullRequestsStats && 
                <Box p={8}>
                    <HStack >
                        <StatsSimple title="Avg: Duration" value={pullRequestsStats.avg_duration}></StatsSimple>
                        <StatsSimple title="Avg: LoC" value={pullRequestsStats.avg_loc}></StatsSimple>
                        <StatsSimple title="Avg: Files Changed" value={pullRequestsStats.avg_files_changed}></StatsSimple>
                        <StatsSimple title="Avg: Comments" value={pullRequestsStats.avg_comments_count}></StatsSimple>
                    </HStack>
                    </Box>
                }
                
                <PrTable onClickOnLine={onClickOnLine} /> 
            </Box>
            
            <PrDrawer isOpen={isOpen} onClose={onClose} currentItem={currentItem} />
        </>
    );
};


const StatsSimple = ({ title, value }: { title: string, value: number}) => {
    return (
      <Box bg={useColorModeValue('white', 'gray.700')} rounded="md" shadow="sm" p="4">
        <Stat size="sm">
          <StatLabel>{title}</StatLabel>
          <StatNumber>{value}</StatNumber>
        </Stat>
      </Box>
    )
  }
  


export default PullRequestsPage;