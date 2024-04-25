import { HStack, Link, useColorModeValue } from "@chakra-ui/react";

interface PagerProps {
    nextPage: () => void;
    prevPage: () => void;
    hasNext: boolean;
    hasPrev: boolean;
}

export default function Pager({nextPage, prevPage, hasNext, hasPrev}:PagerProps) {
    return (
        <HStack width="100%" justifyContent="center" pt={2}>
            <Link onClick={prevPage} cursor="pointer" pointerEvents={hasPrev?"all":"none"} color={!hasPrev?useColorModeValue("blackAlpha.400","whiteAlpha.400"):undefined} >&lt;&nbsp;Previous</Link>
            <Link onClick={nextPage} cursor="pointer" pointerEvents={hasNext?"all":"none"} color={!hasNext?useColorModeValue("blackAlpha.400","whiteAlpha.400"):undefined}>Next&nbsp;&gt;</Link>
        </HStack>
    )
}