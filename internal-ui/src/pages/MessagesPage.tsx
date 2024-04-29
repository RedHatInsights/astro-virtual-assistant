import {
    Breadcrumb,
    BreadcrumbItem, Button,
    PageSection,
} from "@patternfly/react-core";
import {Link, useParams} from "react-router-dom";
import {useMessages} from "../services/messages.ts";
import {LoadingPageSection} from "../components/LoadingPageSection.tsx";
import {SessionComponent} from "../components/SessionComponent.tsx";


export const MessagesPage = () => {

    const {senderId} = useParams();
    const messagesQuery = useMessages(senderId!);
    const isLoading = messagesQuery.isFirstLoad || messagesQuery.isLoading;

    return <>
        <PageSection>
            <Breadcrumb>
                <BreadcrumbItem>
                    Home
                </BreadcrumbItem>
                <BreadcrumbItem>
                    <Link to="/senders">Senders</Link>
                </BreadcrumbItem>
                <BreadcrumbItem>
                    {senderId}
                </BreadcrumbItem>
            </Breadcrumb>
        </PageSection>
        {messagesQuery.isFirstLoad ? <LoadingPageSection /> : <PageSection>
            <ul>
                {messagesQuery.sessions.map(s => (<>
                        <SessionComponent key={s.timestamp} session={s} />
                    <br/>
                </>)
                )}
            </ul>
            <Button onClick={() => messagesQuery.loadMore()} isLoading={isLoading} isDisabled={isLoading}>Load more</Button>
        </PageSection>}
    </>;
};
