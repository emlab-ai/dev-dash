import { Box, Container, Table, TableContainer, Thead, Tr, Th, Tbody, Td, useDisclosure, useColorModeValue, Avatar } from "@chakra-ui/react";
import ScopeFilter from "@src/components/ScopeFilter";
import { useUsersStatsContext } from "@src/providers/usersStatsViewModel";
import { useCallback, useEffect, useState } from "react";
import { UserDetailsDrawer } from "./components/UserDetailsDrawer";
import { useParams, useNavigate } from "react-router-dom";
import { TableCellDuration } from "@src/components/TableCellDuration";


export default function UsersStatsPage() {
    const navigate = useNavigate();
    const { isOpen, onOpen, onClose } = useDisclosure({
        onClose: () => navigate(`/usersstats`)
    })
    const [currentItem, setCurrentItem] = useState<number | undefined>();
    const hoverColor = useColorModeValue("blackAlpha.100", "whiteAlpha.100");
    

    const onClickOnLine = useCallback((id:number) => {
        navigate(`/usersstats/${id}`);
    }, [onOpen, navigate]);

    const { id } = useParams<{ id: string }>();

    useEffect(() => {
        if(id) {
            setCurrentItem(parseInt(id, 10));
            onOpen();
        } else if (isOpen){
            onClose();
        }
    }, [id]);

    const { managerFilter, setManagerFilter, timeFilter, setTimeFilter, usersStats } = useUsersStatsContext();
    return (
        <>
            <Box minH="100vh">
                <ScopeFilter managerFilter={managerFilter} timeFilter={timeFilter} setTimeFilter={setTimeFilter} setManagerFilter={setManagerFilter }  />

                <Container w="100%" maxW="full">
                    <TableContainer>
                    <Table>
                        <Thead>
                            <Tr>
                                <Th></Th>
                                <Th>User</Th>
                                <Th>Team</Th>
                                <Th># of PRs</Th>
                                <Th>Avg: Duration</Th>
                                <Th>Max: Duration</Th>
                                <Th>Avg: LoC</Th>
                                <Th>Max: LoC</Th>
                                <Th>Sum: LoC</Th>
                            </Tr>
                        </Thead>
                        <Tbody>
                            { usersStats.map((stat) => 
                                <Tr key={stat.authorId} onClick={()=>onClickOnLine(stat.authorId)} _hover={{ bg: hoverColor, cursor: "pointer" }}>
                                    <Td><Avatar size="sm" name={stat.user_name}/></Td>
                                    <Td>{stat.user_name}</Td>
                                    <Td>{stat.user_team}</Td>
                                    <Td>{stat.count}</Td>
                                    <Td><TableCellDuration hours={stat.avg_duration}/></Td>
                                    <Td><TableCellDuration hours={stat.max_duration}/></Td>
                                    <Td>{stat.avg_loc}</Td>
                                    <Td>{stat.max_loc}</Td>
                                    <Td>{stat.sum_loc}</Td>
                                </Tr>
                            )
                            }
                            
                        </Tbody>
                    </Table>
                    </TableContainer>
                </Container>
            </Box>
            {<UserDetailsDrawer isOpen={isOpen} onClose={onClose} userId={currentItem} />}
        </>
    )
}