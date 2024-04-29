import {Bullseye, PageSection, Spinner} from "@patternfly/react-core";

export const LoadingPageSection: React.FunctionComponent = () => {
    return <PageSection>
        <Bullseye>
            <Spinner size="xl"/>
        </Bullseye>
    </PageSection>
}
