import { Box, Container, Heading, Tab, TabList, TabPanel, TabPanels, Tabs, Text } from "@chakra-ui/react"
import YooptaEditor, { createYooptaEditor } from '@yoopta/editor';
import Paragraph from '@yoopta/paragraph';
import Blockquote from '@yoopta/blockquote';
import { useMemo } from "react";

const plugins = [Paragraph, Blockquote];

export default function UserPage() {
  const editor = useMemo(() => createYooptaEditor(), []);

  return (
    <Box bg="gray.50" minH="100vh" py="4">
   
      <Tabs>
        <TabList>
          <Tab>Profile</Tab>
          <Tab>Connect</Tab>
          <Tab>Career Path</Tab>
        </TabList>
        <TabPanels>
          <TabPanel>
            <Container w="100%" maxW="full">
                <Heading size="md">Goals</Heading>
                
                <YooptaEditor
                  editor={editor}
                  plugins={plugins}
                />

                <Text size="lg">Results</Text>
                text box
            </Container>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  )
}

