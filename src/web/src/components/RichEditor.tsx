import { YooptaContentValue } from "@yoopta/editor";
import { FC, useMemo, useRef } from "react";
import YooptaEditor, { createYooptaEditor } from "@yoopta/editor";

import Paragraph from '@yoopta/paragraph';
import Blockquote from '@yoopta/blockquote';
import Embed from '@yoopta/embed';
import Link from '@yoopta/link';
import Callout from '@yoopta/callout';
import { NumberedList, BulletedList, TodoList } from '@yoopta/lists';
import { Bold, Italic, CodeMark, Underline, Strike, Highlight } from '@yoopta/marks';
import { HeadingOne, HeadingThree, HeadingTwo } from '@yoopta/headings';
import Code from '@yoopta/code';
import Table from '@yoopta/table';
import Divider from '@yoopta/divider';
import ActionMenuList, { DefaultActionMenuRender } from '@yoopta/action-menu-list';
import Toolbar, { DefaultToolbarRender } from '@yoopta/toolbar';
import LinkTool, { DefaultLinkToolRender } from '@yoopta/link-tool';
import { Flex } from "@chakra-ui/react";

const plugins = [
    Paragraph,
    Table,
    Divider.extend({
        elementProps: {
            divider: (props) => ({
                ...props,
                color: '#007aff',
            }),
        },
    }),
    HeadingOne,
    HeadingTwo,
    HeadingThree,
    Blockquote,
    Callout,
    NumberedList,
    BulletedList,
    TodoList,
    Code,
    Link,
    Embed,
];
const TOOLS = {
    ActionMenu: {
        render: DefaultActionMenuRender,
        tool: ActionMenuList,
    },
    Toolbar: {
        render: DefaultToolbarRender,
        tool: Toolbar,
    },
    LinkTool: {
        render: DefaultLinkToolRender,
        tool: LinkTool,
    },
};

const MARKS = [Bold, Italic, CodeMark, Underline, Strike, Highlight];


export interface RichEditorProps {
    value: YooptaContentValue;
    onChange: (value: YooptaContentValue) => void;
}

export const RichEditor:FC<RichEditorProps> = ({value, onChange}) => {
    const descriptionEditor = useMemo(() => createYooptaEditor(), []);
    const boxRef = useRef<HTMLDivElement>(null);

    return (
        <Flex ref={boxRef} w="500px" position="relative" transform="translateZ(0)">
            <YooptaEditor
                width="400px"
                editor={descriptionEditor}
                plugins={plugins}
                placeholder="Type something"
                tools={TOOLS}
                marks={MARKS}
                value={value}
                selectionBoxRoot={boxRef}
                onChange={onChange}
            />
        </Flex>
    );
}