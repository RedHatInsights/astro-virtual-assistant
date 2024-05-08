import * as React from 'react';
import type {Session} from "../Types.ts";
import {Card, CardBody, CardExpandableContent, CardHeader, CardTitle, Timestamp} from "@patternfly/react-core";
import {MessageBotComponent} from "./MessageBotComponent.tsx";
import {MessageSessionStartedComponent} from "./MessageSessionStartedComponent.tsx";
import {MessageUserComponent} from "./MessageUserComponent.tsx";
import ReactTimeAgo from 'react-time-ago'

interface SessionProps {
    session: Session;
    displaySender?: boolean;
}

export const SessionComponent: React.FunctionComponent<SessionProps> = ({session, displaySender}) => {

    const [isExpanded, setIsExpanded] = React.useState(true);

    return <Card isExpanded={isExpanded}>
        <CardHeader
            isToggleRightAligned
            onExpand={() => setIsExpanded(prev => !prev)}
        >
            <CardTitle>
                Started <ReactTimeAgo timeStyle="round-minute" date={new Date(session.timestamp * 1000)}/> {!session.hasSessionStarted && " (or before) "}
                <Timestamp date={new Date(session.timestamp * 1000)} />
                {displaySender ? (<>
                    <br/> {session.senderId}
                </>) : ''}

            </CardTitle>
        </CardHeader>
        <CardExpandableContent>
            <CardBody>
                {session.messages.map(m => {
                    switch (m.type_name) {
                        case "bot":
                            return <MessageBotComponent key={m.id} message={m} />
                        case "session_started":
                            return <MessageSessionStartedComponent key={m.id} message={m} />
                        case "user":
                            return <MessageUserComponent key={m.id} message={m} />
                    }
                })}
            </CardBody>
        </CardExpandableContent>
    </Card>;
}
