import {
    Breadcrumb,
    BreadcrumbItem, Button,
    PageSection,
} from "@patternfly/react-core";
import {useMessages} from "../services/messages.ts";
import {LoadingPageSection} from "../components/LoadingPageSection.tsx";
import {SessionComponent} from "../components/SessionComponent.tsx";


export const TimelinePage = () => {
    const messagesQuery = useMessages();
    const isLoading = messagesQuery.isFirstLoad || messagesQuery.isLoading;

    return <>
        <PageSection>
            <Breadcrumb>
                <BreadcrumbItem>
                    Home
                </BreadcrumbItem>
                <BreadcrumbItem>
                    Timeline
                </BreadcrumbItem>
            </Breadcrumb>
        </PageSection>
        {messagesQuery.isFirstLoad ? <LoadingPageSection /> : <PageSection>
            <ul>
                {messagesQuery.sessions.map(s => (<>
                        <SessionComponent key={s.timestamp} session={s} displaySender />
                    <br/>
                </>)
                )}
            </ul>
            <Button onClick={() => messagesQuery.loadMore()} isLoading={isLoading} isDisabled={isLoading}>Load more</Button>
        </PageSection>}
    </>;
};
