import React from "react";
import {
    Breadcrumb,
    BreadcrumbItem,
    PageSection,
    Grid,
    GridItem
} from "@patternfly/react-core";
import {Link} from "react-router-dom";
import {AverageNumberofConversations, AverageUserStatistics, NumberOfSessions, SelectFilters, SessionReviewCount, UniqueUsers} from "../components/DashboardComponent.tsx";



export const DashboardPage: React.FunctionComponent = () => {
    return (
        <>
            <PageSection>
                <Breadcrumb>
                    <BreadcrumbItem>Home</BreadcrumbItem>
                    <BreadcrumbItem component={Link} to="/dashboard">Dashboard</BreadcrumbItem>
                </Breadcrumb>
            </PageSection>
            <PageSection>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '10px' }}>
              <div style={{ flex: 1, padding: '10px' }}>
                <Grid hasGutter >
                  <GridItem><SelectFilters/></GridItem>
                </Grid>
              </div>
              <div style={{ flex: 2, padding: '10px' }}>
                <Grid hasGutter span={12}>
                <GridItem><NumberOfSessions/></GridItem>
                <GridItem><SessionReviewCount/></GridItem>
                <GridItem><AverageNumberofConversations/></GridItem>
                <GridItem><AverageUserStatistics/></GridItem>
                <GridItem><UniqueUsers/></GridItem>
                </Grid>
              </div>
            </div>
            </PageSection>
        </>
    );
};

