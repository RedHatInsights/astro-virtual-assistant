import React from "react";
import {
    Breadcrumb,
    BreadcrumbItem, Button,
    Checkbox,
    PageSection,
    PageSectionVariants,
    SearchInput,
    Split,
    SplitItem,
} from "@patternfly/react-core";
import {Link} from "react-router-dom";

import {MessageUserWithSessionData, Session} from "../Types.ts";
import {useMessages} from "../services/messages.ts";
import {LoadingPageSection} from "../components/LoadingPageSection.tsx";
import { UserMessagesTable } from "../components/UserMessagesTable.tsx";

export const UserMessagesPage = () => {

    const messagesQuery = useMessages();
    const isLoading = messagesQuery.isFirstLoad || messagesQuery.isLoading;

    // filters
    const [searchValue, setSearchValue] = React.useState('');
    const [isExternal, setIsExternal] = React.useState<boolean>(false);
    
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
                    return m.data.parse_data.intent.name.includes(searchValue) || m.data.text.includes(searchValue) || m.sender_id.includes(searchValue); 
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
        {messagesQuery.isFirstLoad ? <LoadingPageSection /> : <>
        <PageSection variant={PageSectionVariants.light}>
            <Split hasGutter>
                <SplitItem >
                    <SearchInput
                        placeholder="Search by intent, message, or sender id"
                        value={searchValue}
                        onChange={(_event, value) => setSearchValue(value)}
                        onClear={() => setSearchValue('')}
                    />
                </SplitItem>
                <SplitItem isFilled></SplitItem>
                <SplitItem>
                    <div style={{paddingTop: "10px"}}>
                        <Checkbox
                            id="toggle-external-only"
                            label="External Only"
                            isChecked={isExternal}
                            onChange={(_event, checked) => setIsExternal(checked)}
                        />
                    </div>
                </SplitItem>
            </Split>
        </PageSection>
        <PageSection>
            <UserMessagesTable messages={filteredMessages} />
            <br />
            <Button onClick={() => messagesQuery.loadMore()} isLoading={isLoading} isDisabled={isLoading}>Load more</Button>
        </PageSection></>}
    </>;
};
