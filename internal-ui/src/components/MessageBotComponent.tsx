import type {MessageBot} from "../Types.ts";
import {Text, TextContent, TextVariants} from "@patternfly/react-core";
import Markdown from 'react-markdown'

interface MessageSessionStartedProps {
    message: MessageBot
}

export const MessageBotComponent: React.FunctionComponent<MessageSessionStartedProps> = ({message}) => {

    return (
        <TextContent>
            <Text component={TextVariants.p}>
                <b>Astro:</b> <Markdown>{message.data.text}</Markdown>
            </Text>
        </TextContent>
    );
}
