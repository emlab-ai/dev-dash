import { Container, useDisclosure, Flex } from "@chakra-ui/react";
import { useCallback, useEffect, useState } from "react";
import { UserDetailsDrawer } from "./components/UserDetailsDrawer";
import { useParams, useNavigate } from "react-router-dom";
import { UserStatsTable } from "./components/UserStatsTable";

export default function UsersStatsPage() {
    const navigate = useNavigate();
    const { isOpen, onOpen, onClose } = useDisclosure({
        onClose: () => navigate(`/gitstats/users`)
    })
    const [currentItem, setCurrentItem] = useState<number | undefined>();

    const onClickOnLine = useCallback((row:any) => {
        navigate(`/gitstats/users/${row.id}`);
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

    return (
        <>
            <Flex flexDir="column" w="100%" h="100%" pt={4}>
                <Container w="100%" maxW="full" flex={1} position="relative">
                    <UserStatsTable onClickOnLine={onClickOnLine} />
                </Container>
            </Flex>
            {<UserDetailsDrawer isOpen={isOpen} onClose={onClose} userId={currentItem} />}
        </>
    )
}