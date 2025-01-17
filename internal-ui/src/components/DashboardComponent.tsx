import { useCallback, useEffect, useState } from 'react';
import {
    Checkbox,
    Card,
    Grid,
    GridItem,
    PageSectionVariants,
    PageSection,
    CardTitle,
    CardBody,
    List,
    ListItem,
    CardFooter,
} from '@patternfly/react-core';
import {
    ChartDonut,
    Chart,
    ChartVoronoiContainer,
    ChartAxis,
    ChartGroup,
    ChartLine,
    ChartBar,
} from '@patternfly/react-charts';
import { BalanceScaleIcon, CheckCircleIcon, FilterIcon, OutlinedClockIcon, PowerOffIcon, UserIcon } from '@patternfly/react-icons';

import { getSessionsInRange } from '../services/messages';
import { Session, isTypeMessageUser, isTypeMessageSlot, isTypeMessageBot } from '../Types';
import { CalendarComponent } from './CalendarComponent';
import { LoadingPageSection } from './LoadingPageSection';
import { HelpPopover } from './HelpPopoverComponent';

// for now, will set up pulling from prometheus later
const TRACKING_INTENTS = [
    "nlu_fallback",
    "intent_core_.*",
    "intent_integration_.*",
    "intent_notifications_.*",
    "insights_vulnerability_.*",
    "intent_enable_2fa",
    "intent_disable_2fa",
    "intent_access_.*",
    "intent_favorites_.*",
    "intent_feedback_.*",
    "intent_image_builder_.*",
    "intent_advisor_.*",
    "intent_inventory_.*",
    "intent_access_*",
    "intent_services_offline",
]

const TIME_TO_LOOK_UP_ORG_ADMIN = .25 // quarter hour

const ONE_WEEK_AGO = new Date();
ONE_WEEK_AGO.setDate(ONE_WEEK_AGO.getDate() - 6);

export const DashboardComponent = () => {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [filteredSessions, setFilteredSessions] = useState<Session[]>([]);

    // Stats
    const [sessionCounts, setSessionCounts] = useState<{ x: string; y: number; name: string; }[]>([]);
    const [intentCounts, setIntentCounts] = useState<{ [key: string]: number }>({});
    const [botMessageCount, setBotMessageCount] = useState(0);
    const [userMessageCount, setUserMessageCount] = useState(0);
    const [uniqueSenders, setUniqueSenders] = useState(0);
    const [activeSessions, setActiveSessions] = useState(0);
    const [activeSessionsCount, setActiveSessionsCount] = useState<{ x: string; y: number; name: string; }[]>([]);
    const [inactiveSessionsCount, setInactiveSessionsCount] = useState<{ x: string; y: number; name: string; }[]>([]);
    const [firstTimeUsers, setFirstTimeUsers] = useState(0);
    const [totalConversations, setTotalConversations] = useState(0);
    const [thumbsUp, setThumbsUpCount] = useState(0);
    const [thumbsDown, setThumbsDownCount] = useState(0);
    const [averageSessionTime, setAverageSessionTime] = useState(0);
    // checking which pages were used the most
    const [pagesUsed, setPagesUsed] = useState<{ [key: string]: number }>({});

    const [contactAdminUsage, setContactAdminUsage] = useState(0);
    const [requestTamUsage, setRequestTamUsage] = useState(0);
    const [servicesOfflineUsage, setServicesOfflineUsage] = useState(0);


    // Filters
    const [startDate, setStartDate] = useState<Date>(ONE_WEEK_AGO);
    const [endDate, setEndDate] = useState<Date>(new Date());
    const [toggleState, setToggleState] = useState<{ internal: boolean, external: boolean, orgAdmins: boolean, activeSessions: boolean }>({
        internal: false,
        external: false,
        orgAdmins: false,
        activeSessions: false
    });

    const [isLoading, setIsLoading] = useState(true);

    const calculateCountsPerDay = useCallback(() => {
        const sessionCountByDay: { [key: string]: number } = {};
        const activeSessionCountByDay: { [key: string]: number } = {};

        filteredSessions.forEach((session) => {
            const day = new Date(session.timestamp * 1000).toISOString().split('T')[0];
            if (!sessionCountByDay[day]) {
                sessionCountByDay[day] = 0;
            }
            sessionCountByDay[day]++;

            if (!activeSessionCountByDay[day]) {
                activeSessionCountByDay[day] = 0;
            }

            session.messages.filter(isTypeMessageUser).some((msg) => {
                if (msg.data.text !== "/intent_core_session_start") {
                    activeSessionCountByDay[day]++;
                    return true;
                }
                return false;
            });
        });

        const sessionCountsArray = [];
        const activeSessionCountsArray = [];
        const inactiveSessionCountsArray = [];
        const currentDate = new Date(startDate);
        while (currentDate <= endDate) {
            const day = currentDate.toISOString().split('T')[0];
            sessionCountsArray.push({
                x: day.toString(),
                y: sessionCountByDay[day] || 0,
                name: "Total"
            });
            activeSessionCountsArray.push({
                x: day.toString(),
                y: activeSessionCountByDay[day] || 0,
                name: "Active"
            });
            inactiveSessionCountsArray.push({
                x: day.toString(),
                y: (sessionCountByDay[day] || 0) - (activeSessionCountByDay[day] || 0),
                name: "Inactive"
            });
            currentDate.setDate(currentDate.getDate() + 1);
        }

        setSessionCounts(sessionCountsArray);
        setActiveSessionsCount(activeSessionCountsArray);
        setInactiveSessionsCount(inactiveSessionCountsArray);
    }, [filteredSessions, startDate, endDate]);

    // filter messages and calculate totals
    useEffect(() => {
        let activeSessions = 0;
        const filtered = sessions.filter((session) => {
            let orgAdmin = false;
            let active = false;
            session.messages.filter(isTypeMessageUser).forEach((msg) => {
                if (msg.data.text === "/intent_core_session_start") {
                    orgAdmin = msg.data.metadata.is_org_admin;
                }
                // if there was a different user message, the session was active
                else if (!active) active = true;
            });
            const internal = session.messages.filter(isTypeMessageSlot).filter(msg => msg.data.name === 'is_internal').some(msg => msg.data.value);

            if ((toggleState.internal && !internal)
                || (toggleState.external && internal)
                || (toggleState.orgAdmins && !orgAdmin)
                || (toggleState.activeSessions && !active)) {
                return false;
            }

            if (active) {
                activeSessions++;
            }

            return true;
        });

        setFilteredSessions(filtered);
        setActiveSessions(activeSessions);

        let thumbsUp = 0;
        let thumbsDown = 0;

        let botMessageCount = 0;
        let userMessageCount = 0;
        let conversationCount = 0;
        let firstTimeUsers = 0;

        let contactAdminUsage = 0;
        let requestTamUsage = 0;
        let servicesOfflineUsage = 0;

        let durations = 0; // total time in all filtered sessions

        const intentCounts: { [key: string]: number } = {};
        const pagesUsed: { [key: string]: number } = {};

        filtered.forEach((session) => {
            session.messages.forEach((msg) => {
                // the slot closing_got_help is recorded multiple times for each feedback in the events
                // why? I don't know!
                if (isTypeMessageBot(msg)) {
                    if (msg.data.metadata.utter_action === 'utter_closing_got_help_yes') {
                        thumbsUp++;
                    } else if (msg.data.metadata.utter_action === 'utter_closing_got_help_no') {
                        thumbsDown++;
                    }

                    if (msg.data.metadata.utter_action === 'utter_ask_closing_got_help') {
                        conversationCount++;
                    }

                    if (msg.data.metadata.utter_action === 'utter_core_first_time') {
                        firstTimeUsers++;
                    }
                    botMessageCount++;
                } else if (isTypeMessageUser(msg)) {
                    const intentName = msg.data.parse_data.intent.name;
                    const matchedIntent = TRACKING_INTENTS.find((intent) =>
                        intentName.match(intent)
                    );

                    if (matchedIntent) {
                        if (!intentCounts[matchedIntent]) {
                            intentCounts[matchedIntent] = 0;
                        }
                        intentCounts[matchedIntent]++;
                    }

                    if (intentName === 'intent_access_contact_admin') {
                        contactAdminUsage++;
                    }
                    if (intentName === 'intent_access_request_tam') {
                        requestTamUsage++;
                    }
                    if (intentName === 'intent_services_offline') {
                        servicesOfflineUsage++;
                    }

                    userMessageCount++;
                } else if (isTypeMessageSlot(msg)) {
                    if (msg.data.name === 'current_url') {
                        const url = msg.data.value;
                        console.log(url);
                        if (typeof url !== 'string') {
                            return
                        }
                        if (!pagesUsed[url]) {
                            pagesUsed[url] = 0;
                        }
                        pagesUsed[url]++;
                    }
                }
            });

            durations += session.lastTimestamp - session.timestamp;
        });

        setBotMessageCount(botMessageCount);
        setUserMessageCount(userMessageCount);
        setTotalConversations(conversationCount);
        setFirstTimeUsers(firstTimeUsers);

        setIntentCounts(intentCounts);
        setPagesUsed(pagesUsed);

        setContactAdminUsage(contactAdminUsage);
        setRequestTamUsage(requestTamUsage);
        setServicesOfflineUsage(servicesOfflineUsage);

        const totalDurationInMinutes = (durations / 1000) / 60;
        setAverageSessionTime(Math.floor(totalDurationInMinutes / filtered.length));

        const senders = new Set(filtered.map((session) => session.senderId));
        setUniqueSenders(senders.size);

        setThumbsUpCount(thumbsUp);
        setThumbsDownCount(thumbsDown);

        calculateCountsPerDay();

        setIsLoading(false);
    }, [toggleState, sessions, calculateCountsPerDay]);

    useEffect(() => {
        setIsLoading(true);
        const fetchMessages = async () => {
            const start = Math.floor(new Date(startDate.setHours(0, 0, 0, 0)).getTime() / 1000);
            const endDateEndOfDay = new Date(endDate);
            endDateEndOfDay.setHours(23, 59, 59, 999);
            const end = Math.floor(endDateEndOfDay.getTime() / 1000);

            const sessionsInRange = await getSessionsInRange(undefined, start, end);
            setSessions(sessionsInRange);
        };
        fetchMessages();
    }, [startDate, endDate]);

    return (
        <PageSection variant={PageSectionVariants.light} isWidthLimited >
            <Grid hasGutter >
                <GridItem span={3} rowSpan={4}>
                    <CalendarComponent
                        startDate={startDate}
                        endDate={endDate}
                        updateDateRange={(start, end) => {
                            setStartDate(start);
                            setEndDate(end);
                        }}
                    />
                    <Card>
                        <CardTitle>Filters <FilterIcon /></CardTitle>
                        <CardBody>
                            <Checkbox
                                label="Internal"
                                isChecked={toggleState.internal}
                                onChange={() => {
                                    setToggleState(prev => (
                                        {
                                            ...prev,
                                            internal: !prev.internal,
                                            external: prev.internal && prev.external
                                        }
                                    ));
                                }}
                                id="toggle-internal"
                            />
                            <Checkbox
                                label="External"
                                isChecked={toggleState.external}
                                onChange={() => {
                                    setToggleState(prev => (
                                        {
                                            ...prev,
                                            internal: prev.internal && prev.external,
                                            external: !prev.external
                                        }
                                    ));
                                }}
                                id="toggle-external"
                            />
                            <Checkbox
                                label="Org Admins"
                                isChecked={toggleState.orgAdmins}
                                onChange={() => {
                                    setToggleState(prev => (
                                        {
                                            ...prev,
                                            orgAdmins: !prev.orgAdmins
                                        }
                                    ));
                                }}
                                id="toggle-org-admins"
                            />
                            <Checkbox
                                label="Active Sessions"
                                isChecked={toggleState.activeSessions}
                                onChange={() => {
                                    setToggleState(prev => (
                                        {
                                            ...prev,
                                            activeSessions: !prev.activeSessions
                                        }
                                    ));
                                }}
                                id="toggle-active-sessions"
                            />
                            {isLoading && <LoadingPageSection />}
                        </CardBody>
                    </Card>
                </GridItem>
                <GridItem span={2} rowSpan={1}>
                    <Card>
                        <ChartDonut
                            data={[
                                { x: 'Positive', y: thumbsUp },
                                { x: 'Negative', y: thumbsDown }
                            ]}
                            title={Math.ceil((thumbsUp / (thumbsUp + thumbsDown)) * 100) + '%'}
                            subTitle="Positive feedback"
                            constrainToVisibleArea
                            labels={({ datum }) => `${datum.x}: ${datum.y}`}
                            themeColor='cyan'
                        />
                    </Card>
                </GridItem>
                <GridItem span={2} rowSpan={1}>
                    <Card>
                        <ChartDonut
                            data={[
                                { x: 'Users', y: uniqueSenders },
                            ]}
                            title={uniqueSenders.toString()}
                            subTitle="User"
                            constrainToVisibleArea
                            themeColor='green'
                            labels={({ datum }) => `${datum.x}: ${datum.y}`}
                        />
                    </Card>
                </GridItem>
                <GridItem span={2} rowSpan={1}>
                    <Card>
                        <ChartDonut
                            data={[
                                { x: 'Bot', y: botMessageCount },
                                { x: 'User', y: userMessageCount }
                            ]}
                            title={(botMessageCount + userMessageCount).toString()}
                            subTitle="Messages"
                            constrainToVisibleArea
                            labels={({ datum }) => `${datum.x}: ${datum.y}`}
                            themeColor='multi'
                        />
                    </Card>
                </GridItem>
                <GridItem span={2} rowSpan={1}>
                    <Card isFullHeight isLarge>
                        <CardBody component='strong'>
                            <List isPlain iconSize="large">
                                <ListItem icon={<CheckCircleIcon />}>{totalConversations} Conversations</ListItem>
                                {contactAdminUsage > 0 &&
                                    <ListItem icon={<CheckCircleIcon />}>{contactAdminUsage * TIME_TO_LOOK_UP_ORG_ADMIN} Engineering Hours Saved
                                        <HelpPopover
                                            title="What does this include?"
                                            content="This considers the time it takes to look up an org admin and contact them."
                                        />
                                    </ListItem>
                                }
                                <ListItem icon={<OutlinedClockIcon />}>{averageSessionTime} Minutes Active on Average</ListItem>
                                <ListItem icon={<BalanceScaleIcon />}>{Math.floor(((userMessageCount - (intentCounts["nlu_fallback"] || 0)) / userMessageCount) * 100)}% Intents Recognized</ListItem>
                                <ListItem icon={<UserIcon />}>{firstTimeUsers} First Time Users</ListItem>
                                {!toggleState.activeSessions &&
                                    <ListItem icon={<PowerOffIcon />}>{filteredSessions.length - activeSessions} Inactive Sessions
                                        <HelpPopover
                                            title="When is a session inactive?"
                                            content="If a user did not send a message after opening the assistant, the session has been inactive."
                                        />
                                    </ListItem>
                                }
                            </List>
                        </CardBody>
                    </Card>
                </GridItem>
                <GridItem span={4} rowSpan={4}>
                    <Card>
                        <CardTitle>{filteredSessions.length} Sessions</CardTitle>
                        <Chart
                            ariaTitle="Sessions over time"
                            containerComponent={<ChartVoronoiContainer labels={({ datum }) => `${datum.x}: ${datum.y} ${datum.name}`} />}
                            name="usage"
                            legendData={[{ name: 'Total' }, { name: "Active" }, { name: 'Inactive', symbol: { type: 'dash' } }]}
                            legendOrientation="horizontal"
                            legendPosition="bottom"
                        >
                            {/* do not show dates */}
                            <ChartAxis tickValues={[]} />
                            <ChartAxis dependentAxis showGrid />
                            <ChartGroup>
                                <ChartLine
                                    data={sessionCounts}
                                    interpolation="monotoneX"
                                />
                                <ChartLine
                                    data={activeSessionsCount}
                                    interpolation="monotoneX"
                                />
                                <ChartLine
                                    data={inactiveSessionsCount}
                                    style={{
                                        data: {
                                            strokeDasharray: '3,3'
                                        }
                                    }}
                                    interpolation="monotoneX"
                                />
                            </ChartGroup>
                        </Chart>
                    </Card>
                </GridItem>
                <GridItem span={4} rowSpan={4}>
                    <Card>
                        <CardTitle>Intents</CardTitle>
                        <Chart
                            ariaTitle="Intents"
                            containerComponent={<ChartVoronoiContainer labels={({ datum }) => `${datum.y} ${datum.x}`} />}
                            name="by_intent"
                            themeColor="multi"
                        >
                            <ChartAxis tickValues={[]} />
                            <ChartAxis dependentAxis showGrid />
                            <ChartGroup>
                                {Object.entries(intentCounts).map(([key, value]) => (
                                    <ChartBar
                                        data={[{ x: key, y: value }]}
                                    />
                                ))}
                            </ChartGroup>
                        </Chart>
                        <CardFooter component="strong">
                            Usage
                            <List>
                                <ListItem>Request TAM: {requestTamUsage}</ListItem>
                                <ListItem>Contact Admin: {contactAdminUsage}</ListItem>
                                <ListItem>Services Offline: {servicesOfflineUsage}</ListItem>
                            </List>
                        </CardFooter>
                    </Card>
                </GridItem>
                <GridItem span={4} rowSpan={4}>
                    <Card>
                        <CardTitle>Pages users talk to the bot on</CardTitle>
                        <Chart
                            ariaTitle="Pages"
                            containerComponent={<ChartVoronoiContainer labels={({ datum }) => `${datum.y} ${datum.x}`} />}
                            name="by_page"
                            themeColor="multi"
                        >
                            <ChartAxis tickValues={[]} />
                            <ChartAxis dependentAxis showGrid />
                            <ChartGroup>
                                {Object.entries(pagesUsed).map(([key, value]) => (
                                    <ChartBar
                                        data={[{ x: key, y: value }]}
                                    />
                                ))}
                            </ChartGroup>
                        </Chart>
                    </Card>
                </GridItem>
            </Grid>
        </PageSection>
    );
};
