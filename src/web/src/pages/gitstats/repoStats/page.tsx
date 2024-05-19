import { Container, useDisclosure, Flex } from "@chakra-ui/react";
import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { RepoStatsTable } from "./components/RepoStatsTable";

export default function UsersStatsPage() {
    const navigate = useNavigate();
    const { isOpen, onOpen, onClose } = useDisclosure({
        onClose: () => navigate(`/usersstats`)
    })
    const [currentItem, setCurrentItem] = useState<number | undefined>();

    const onClickOnLine = useCallback((row:any) => {
        navigate(`/gitstats/repositories/${row.id}`);
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
                    <RepoStatsTable onClickOnLine={onClickOnLine} />
                </Container>
            </Flex>
        </>
    )
}