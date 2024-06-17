import { Box, Flex, HStack, Heading, IconButton, List, ListIcon, ListItem, Menu, MenuButton, MenuItem, MenuList, Text,  useColorModeValue, useDisclosure  } from '@chakra-ui/react'
import { BiMenu } from 'react-icons/bi'
import { AiOutlineHome, AiOutlineSetting, AiOutlineUser, AiFillGithub } from 'react-icons/ai'

import { Head, ThemeToggle } from '@components/index'
import { BrandName } from '@src/constants'
import { Link, Outlet } from 'react-router-dom'
import { useAuth0 } from '@auth0/auth0-react'



type ListItem = {
    text?: string
    icon: React.ElementType,
    link: string   
}

const listItems: ListItem[] = [
  {
    text: 'Home',
    icon: AiOutlineHome,
    link: '/'
  },
  {
    text: 'GitHub PRs',
    icon: AiFillGithub,
    link: '/gitstats'
  },
  {
    text: 'Settings',
    icon: AiOutlineSetting,
    link: '/settings'
  },
]

export default function Layout() {
  const { getButtonProps, isOpen } = useDisclosure()
  const buttonProps = getButtonProps()
  const {logout} = useAuth0();
  return (
    <>
        <Head>
            <title>emlab.ai</title>
        </Head>
        <Flex as="nav" alignItems="center" justifyContent="space-between" h='16' py='2.5' pr="2.5">
            <HStack spacing={2}>

                <img src="/public/logo.svg" alt="Logo" width="36px" style={{marginLeft: 12}}/>
                <IconButton {...buttonProps} _active='none' _focus='none' _hover='none' fontSize="18px" variant='ghost' icon={<BiMenu />} aria-label='open menu'/>
                <Heading as='h1' size="md">{BrandName}</Heading>
            </HStack>
            <HStack spacing="1">
                <ThemeToggle />
                <Menu>
                  <MenuButton
                    as={IconButton}
                    isRound={true}
                    size="lg"
                    aria-label='user icon'
                    icon={<AiOutlineUser />}
                  />
                  <MenuList>
                    <MenuItem onClick={()=>logout()}>Logout</MenuItem>
                  </MenuList>
                </Menu>
            </HStack>
        </Flex>
        <HStack align="start" spacing={0}>
            <Box as="aside" minH="90vh" w={isOpen ? 72 : 12} borderRight="2px" borderColor={useColorModeValue('gray.200', 'gray.900')} transition="width 0.25s ease"> 
                <List spacing={0} p="0.5">
                    {
                    listItems.map(item => (<ListElement key={item.text} icon={item.icon} text={isOpen ? item.text : '' } link={item.link} />))
                    }
                </List>
            </Box>
            <Flex as="main" w='full' minH="90vh" bg={useColorModeValue('gray.50', 'gray.900')}>
              <Box width="100%" h="calc(100vh - 64px)" position="relative">
                  <Outlet/>
              </Box>
            </Flex>
        </HStack>
    </>
  )
}

const ListElement = ({ icon, text, link }: ListItem) => {
  return (
    <Link to={link}>
        <ListItem as={HStack} spacing={0} h="10" pl="2.5" cursor="pointer" _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }} rounded="md">
        <ListIcon boxSize={5} as={icon} />
        {
            text && <Text>{text}</Text>
        }
        </ListItem>
    </Link>
  )
}