import { Box, Stat, StatLabel, StatNumber, useDisclosure, useColorModeValue, HStack } from '@chakra-ui/react';
import { PullRequest, usePullRequestsContext } from '@src/providers/pullRequestsViewModel';
import { useCallback, useState } from 'react';
import PrDrawer from './components/PrDrawer';
import PrTable from './components/PrTable';

const PullRequestsPage = () => {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [currentItem, setCurrentItem] = useState<PullRequest | null>(null);

  const onClickOnLine = useCallback((pr: PullRequest) => {
    console.log('clicked on line', pr.id);
    setCurrentItem(pr);
    onOpen();
  }, [onOpen]);

  const { pullRequestsStats } = usePullRequestsContext();

  return (
    <>
      <Box id="prs" display="grid" position="absolute" pl={4} pr={4} top={0} bottom={0} left={0} right={0} gridTemplateRows="auto 1fr">
        <Box p={2}>
          <HStack >
            <StatsSimple title="Count" value={pullRequestsStats?.count ?? 0}></StatsSimple>
            <StatsSimple title="Avg: Duration" value={pullRequestsStats?.avg_duration ?? 0}></StatsSimple>
            <StatsSimple title="Avg: LoC" value={pullRequestsStats?.avg_loc ?? 0}></StatsSimple>
            <StatsSimple title="Avg: Files Changed" value={pullRequestsStats?.avg_files_changed ?? 0}></StatsSimple>
            <StatsSimple title="Avg: Comments" value={pullRequestsStats?.avg_comments_count ?? 0}></StatsSimple>
          </HStack>
        </Box>
        <Box position="relative">
          <PrTable onClickOnLine={onClickOnLine} />
        </Box>
      </Box>

      <PrDrawer isOpen={isOpen} onClose={onClose} currentItem={currentItem} />
    </>
  );
};

const StatsSimple = ({ title, value }: { title: string, value: number }) => {
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