import type {MessageSessionStarted} from "../Types.ts";
import {Text, TextContent, TextVariants} from "@patternfly/react-core";

interface MessageSessionStartedProps {
    message: MessageSessionStarted
}

export const MessageSessionStartedComponent: React.FunctionComponent<MessageSessionStartedProps> = () => {
    return <TextContent>
        <Text component={TextVariants.p}>
            <b> Session started</b>
        </Text>
    </TextContent>;
}
