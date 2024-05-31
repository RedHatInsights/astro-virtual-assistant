import {
    Breadcrumb,
    BreadcrumbItem, Button,
    PageSection,
} from "@patternfly/react-core";
import {Link} from "react-router-dom";

import {MessageUser, Session} from "../Types.ts";
import {useMessages} from "../services/messages.ts";
import {LoadingPageSection} from "../components/LoadingPageSection.tsx";
import { UserMessages } from "../components/UserMessages.tsx";


export const UserMessagesPage = () => {

    const messagesQuery = useMessages();
    const isLoading = messagesQuery.isFirstLoad || messagesQuery.isLoading;

    const filterMessagesFromSessions = (sessions: ReadonlyArray<Session>) => {
        const mess: MessageUser[] = [];
        sessions.forEach(s => {
            s.messages.forEach(m => {
                if (m.type_name === "user" && !m.data.text.startsWith("/")) mess.push(m)
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
