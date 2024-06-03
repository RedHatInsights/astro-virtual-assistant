import {
    Breadcrumb,
    BreadcrumbItem, Button,
    PageSection,
} from "@patternfly/react-core";
import {Link} from "react-router-dom";

import {MessageUserWithSessionData, Session} from "../Types.ts";
import {useMessages} from "../services/messages.ts";
import {LoadingPageSection} from "../components/LoadingPageSection.tsx";
import { UserMessages } from "../components/UserMessages.tsx";


export const UserMessagesPage = () => {

    const messagesQuery = useMessages();
    const isLoading = messagesQuery.isFirstLoad || messagesQuery.isLoading;

    const filterMessagesFromSessions = (sessions: ReadonlyArray<Session>) => {
        const mess: MessageUserWithSessionData[] = [];
        sessions.forEach(s => {
            let is_internal = false;
            s.messages.forEach(m => {
                if (m.type_name === "slot" && m.data.name === "is_internal" && m.data.value === true) {
                    is_internal = true;
                }
            });
            s.messages.forEach(m => {
                if (m.type_name === "user" && !m.data.text.startsWith("/")) {
                    const with_session_data = m as MessageUserWithSessionData;
                    with_session_data.is_internal = is_internal;
                    mess.push(with_session_data)
                }
            });
        });
        return mess;
    }

    return <>
        <PageSection>
            <Breadcrumb>
                <BreadcrumbItem>
                    Home
                </BreadcrumbItem>
                <BreadcrumbItem>
                    <Link to="/messages">Messages</Link>
                </BreadcrumbItem>
            </Breadcrumb>
        </PageSection>
        {messagesQuery.isFirstLoad ? <LoadingPageSection /> : <PageSection>
            <ul>
                <UserMessages messages={filterMessagesFromSessions(messagesQuery.sessions)} />
            </ul>
            <Button onClick={() => messagesQuery.loadMore()} isLoading={isLoading} isDisabled={isLoading}>Load more</Button>
        </PageSection>}
    </>;
};
