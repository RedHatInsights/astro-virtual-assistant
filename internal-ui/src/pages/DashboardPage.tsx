import React from "react";
import {
    Breadcrumb,
    BreadcrumbItem,
    PageSection,
} from "@patternfly/react-core";
import {Link} from "react-router-dom";
import {DashboardComponent} from "../components/DashboardComponent.tsx";



export const DashboardPage: React.FunctionComponent = () => {
    return (
        <>
            <PageSection>
                <Breadcrumb>
                    <BreadcrumbItem>Home</BreadcrumbItem>
                    <BreadcrumbItem component={Link} to="/dashboard">Dashboard</BreadcrumbItem>
                </Breadcrumb>
            <div style={{ display: 'flex', justifyContent: 'space-between', overflowY: 'auto', gap: '5px', marginTop: '10px' }}>
            <DashboardComponent/>
            </div>
            </PageSection>
        </>
    );
};

