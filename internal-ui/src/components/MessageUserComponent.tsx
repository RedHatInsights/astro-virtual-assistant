import * as React from 'react';
import type {MessageUser} from "../Types.ts";
import {Text, TextContent, TextVariants, Timestamp} from "@patternfly/react-core";

interface MessageSessionStartedProps {
    message: MessageUser
}

export const MessageUserComponent: React.FunctionComponent<MessageSessionStartedProps> = ({message}) => {
    // Filter out our know commands that are sent by the UI
    if (message.data.text === "/intent_core_session_start") {
        return;
    }

    return (
        <TextContent>
            <Text component={TextVariants.p}>
                <b>User:</b> {message.data.text}
                <div>
                    &nbsp;
                    ({message.data.parse_data.intent.name})
                    &nbsp;
                    <Timestamp date={new Date(message.timestamp * 1000)} />
                </div>
            </Text>
        </TextContent>
    );
}
