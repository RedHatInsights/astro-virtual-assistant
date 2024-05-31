import {
    Breadcrumb,
    BreadcrumbItem, Button,
    PageSection,
} from "@patternfly/react-core";
import {Link} from "react-router-dom";

import {MessageUser, Session} from "../Types.ts";
import {useMessages} from "../services/messages.ts";
import {LoadingPageSection} from "../components/LoadingPageSection.tsx";
import { UniqueMessages } from "../components/UniqueMessages.tsx";


export const UniqueMessagesPage = () => {

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
                    <Link to="/unique">Unique Messages</Link>
                </BreadcrumbItem>
            </Breadcrumb>
        </PageSection>
        {messagesQuery.isFirstLoad ? <LoadingPageSection /> : <PageSection>
            <ul>
                <UniqueMessages messages={filterMessagesFromSessions(messagesQuery.sessions)} />
            </ul>
            <Button onClick={() => messagesQuery.loadMore()} isLoading={isLoading} isDisabled={isLoading}>Load more</Button>
        </PageSection>}
    </>;
};
