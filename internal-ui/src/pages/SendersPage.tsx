import {Breadcrumb, BreadcrumbItem, PageSection} from "@patternfly/react-core";
import {useSenders} from "../services/senders.ts";
import {Senders} from "../components/Senders.tsx";
import {LoadingPageSection} from "../components/LoadingPageSection.tsx";

export const SendersPage = () => {

    const sendersQuery = useSenders();

    return <>
        <PageSection>
            <Breadcrumb>
                <BreadcrumbItem>
                    Home
                </BreadcrumbItem>
                <BreadcrumbItem>
                    Senders
                </BreadcrumbItem>
            </Breadcrumb>
        </PageSection>
        {!sendersQuery.isLoading ? <PageSection><Senders senders={sendersQuery.data!} /> </PageSection>: <LoadingPageSection />}
    </>;
};
