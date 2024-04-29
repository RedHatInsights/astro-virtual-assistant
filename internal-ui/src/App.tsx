import { useState } from 'react'
import {
    Masthead,
    MastheadToggle, Nav, NavItem, NavList, Page,
    PageSidebar,
    PageSidebarBody,
    PageToggleButton
} from '@patternfly/react-core';
import {BarsIcon} from "@patternfly/react-icons";
import {
    Outlet,
    Link,
    useLocation
} from "react-router-dom";
import '@patternfly/react-core/dist/styles/base.css';


function App() {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

    const onSidebarToggle = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    const location = useLocation();

    const header = (
        <Masthead>
            <MastheadToggle>
                <PageToggleButton
                    variant="plain"
                    aria-label="Global navigation"
                    isSidebarOpen={isSidebarOpen}
                    onSidebarToggle={onSidebarToggle}
                    id="vertical-nav-toggle"
                >
                    <BarsIcon />
                </PageToggleButton>
            </MastheadToggle>
        </Masthead>
    );

    const sidebar = (
        <PageSidebar isSidebarOpen={isSidebarOpen} id="vertical-sidebar">
            <PageSidebarBody>
                <Nav>
                    <NavList>
                        <NavItem itemId="conversations" isActive={location.pathname.startsWith("/senders")}>
                            <Link to={"senders"}>
                                Senders
                            </Link>
                        </NavItem>
                    </NavList>
                </Nav>
            </PageSidebarBody>
        </PageSidebar>
    );


    return (
        <Page header={header} sidebar={sidebar}>
            <Outlet />
        </Page>
    );
}

export default App
