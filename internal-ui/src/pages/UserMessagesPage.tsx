import React from "react";
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

    // filters
    const [searchValue, setSearchValue] = React.useState('');
    const [isExternal, setIsExternal] = React.useState<boolean>(false);

    const updateFilters = (isExternal: boolean, searchValue: string) => {
        setIsExternal(isExternal);
        setSearchValue(searchValue);
    }
    
    const filterMessagesFromSessions = React.useCallback((sessions: ReadonlyArray<Session>) => {
        const mess: MessageUserWithSessionData[] = [];
        sessions.forEach(s => {
            let is_internal = false;
            s.messages.forEach(m => {
                if (m.type_name === "slot" && m.data.name === "is_internal") {
                    if (m.data.value === true) {
                        is_internal = true;
                    }
                    return;
                }
            });

            if (isExternal && is_internal) {
                return;
            }

            const filtered = s.messages.filter(m => {
                if (m.type_name !== "user" || m.data.text.startsWith("/")) {
                    return false;
                }

                if (searchValue !== "") {
                    return m.data.parse_data.intent.name.includes(searchValue) || m.data.text.includes(searchValue); 
                }
                return true;
            });

            filtered.forEach(m => {
                const with_session_data = m as MessageUserWithSessionData;
                with_session_data.is_internal = is_internal;
                mess.push(with_session_data);
            });
        });

        setFilteredMessages(mess);
    }, [isExternal, searchValue]);

    const [filteredMessages, setFilteredMessages] = React.useState<MessageUserWithSessionData[]>([]);

    React.useEffect(() => {
        filterMessagesFromSessions(messagesQuery.sessions);
    }, [messagesQuery.sessions, isExternal, searchValue, filterMessagesFromSessions]);

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
                <UserMessages messages={filteredMessages} isExternal={isExternal} searchValue={searchValue} updateFilters={updateFilters} />
            </ul>
            <br />
            <Button onClick={() => messagesQuery.loadMore()} isLoading={isLoading} isDisabled={isLoading}>Load more</Button>
        </PageSection>}
    </>;
};
