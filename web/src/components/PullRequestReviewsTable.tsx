import { Avatar, Text, Box, HStack, Table, TableContainer, Tag, Tbody, Td, Th, Thead, Tr, Tooltip, Link } from '@chakra-ui/react';
import { useCallback, useEffect, useState, createContext, useContext } from 'react';
import { TableCellDate } from './TableCellDate';
import Pager from './Pager';

interface PullRequestReviewsModel {
    reviews: PullRequestReview[] | null;
    nextReviewPage: () => void;
    prevReviewPage: () => void;
    hasNextReviewPage: boolean;
    hasPrevReviewPage: boolean;
}

interface PullRequestReview {
    id:number;
    prUrl: string;
    state: string;
    createdAt: Date;
    publishedAt: Date;
    author: string;
    authorId: number;
    author_name: string;
    body: string;
}

export const usePullRequestReviewsModel = (id:number, startDate: string, endDate:string): PullRequestReviewsModel => {
    const [reviews, setReviews] = useState<PullRequestReview[]>([]);
    const [reviewsBefore, setReviewsBefore] = useState<string|null>(null);
    const [reviewsAfter, setReviewsAfter] = useState<string|null>(null);

    const fetchReviewsAsync = useCallback(async (userId:number, startDateStr: string, endDateStr: string, before?: string, after?: string) => {
        try {
            let pageStr = '';
            if (!!before) {
                pageStr = `&before=${before}`;
            } else if (!!after) {
                pageStr = `&after=${after}`;
            }
            const response = await fetch(`/api/users/${userId}/reviews?start_date=${startDateStr}&end_date=${endDateStr}&page_size=10${pageStr}`);
            const result = await response.json();

            setReviews(result.data);
            setReviewsBefore(result.before);
            setReviewsAfter(result.after);
        } catch (error) {
            console.error('Error fetching reviews', error);
        }
    }, []);

    useEffect(() => {
        fetchReviewsAsync(id, startDate, endDate);
    }, [id, endDate, startDate])

   
    const nextReviewPage = useCallback(async () => {
        if (!reviewsAfter) {
            return;
        }
        fetchReviewsAsync(id, startDate, endDate, undefined, reviewsAfter);
    }, [reviewsAfter, id, startDate, endDate, fetchReviewsAsync]);

    const prevReviewPage = useCallback(async () => {
        if (!reviewsBefore) {
            return;
        }
        fetchReviewsAsync(id, startDate, endDate, reviewsBefore);
    }, [reviewsBefore, id, startDate, endDate, fetchReviewsAsync]);

    return {
        reviews,
        nextReviewPage,
        prevReviewPage,
        hasNextReviewPage: !!reviewsAfter,
        hasPrevReviewPage: !!reviewsBefore
    };
};


// Create the context
const PullRequestReviewsContext: React.Context<PullRequestReviewsModel | null> = createContext<PullRequestReviewsModel | null>(null);

// Create a custom hook to access the context
export const usePullRequestReviewsContext = (): PullRequestReviewsModel => {
    const context = useContext(PullRequestReviewsContext);
    if (!context) {
        throw new Error('useDashboardContext must be used within a DashboardProvider');
    }
    return context;
};

// Create the provider component
export const PullRequestReviewsProvider: React.FC<{ id:number, startDate:string, endDate:string, children: React.ReactNode }> = ({id, children, startDate: start_date, endDate: end_date }) => {
    const model = usePullRequestReviewsModel(id, start_date, end_date);

    return <PullRequestReviewsContext.Provider value={model}>
        {children}
    </PullRequestReviewsContext.Provider>
};

interface PullRequestReviewsTableProps {
    userId: number;
    startDate: string;
    endDate: string;
}

export const PullRequestReviewsTable = ({userId, startDate, endDate}: PullRequestReviewsTableProps) => {

    return <PullRequestReviewsProvider id={userId} startDate={startDate} endDate={endDate}>
        <PullRequestReviewsTableImpl />
    </PullRequestReviewsProvider>
}

const PullRequestReviewsTableImpl = () => {
    const {reviews, nextReviewPage, prevReviewPage, hasNextReviewPage, hasPrevReviewPage} = usePullRequestReviewsContext();

    return <><TableContainer>
        <Table size="sm" width="100%">
            <Thead>
                <Tr>
                    <Th w="25px"></Th>
                    <Th w="100px">State</Th>
                    <Th w="200px">Repo</Th>
                    <Th>Text</Th>
                </Tr>
            </Thead>
            <Tbody>
                {reviews && reviews.map((review:PullRequestReview) => (
                    <Tr key={review.id}> 
                        <Td><Avatar size="sm" name={review.author_name}/></Td>
                        <Td><ReviewState date={review.createdAt} state={review.state}/></Td>                        
                        <Td> 
                            <Tooltip label={review.prUrl} aria-label="PR URL" placement="top">
                                <Link href={review.prUrl} target="_blank" rel="noopener noreferrer">
                                    <Text isTruncated >{getRepoNameFromUrl(review.prUrl)}</Text>
                                </Link> 
                            </Tooltip>
                        </Td>
                        <Td><Box flex={1}>{review.body}</Box></Td>
                    </Tr>
                ))}
            </Tbody>
        </Table>
    </TableContainer>
    <Pager nextPage={nextReviewPage} prevPage={prevReviewPage} hasNext={hasNextReviewPage} hasPrev={hasPrevReviewPage}/>
    </>
}

const ReviewState = ({date, state}: {date: Date, state: string}) => {

    return <HStack>
        <Box minW="100px">
            <Tag size="sm" colorScheme={state === 'APPROVED'?'green':'red'}>{state}</Tag>
        </Box>
        <TableCellDate date={date}/>
    </HStack>
}

function getRepoNameFromUrl(url: string) {
    const parts = url.split('/');
    return parts[4];
}