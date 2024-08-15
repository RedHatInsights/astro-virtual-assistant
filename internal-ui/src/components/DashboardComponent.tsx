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
import { CheckCircleIcon } from '@patternfly/react-icons';

import { getSessionsInRange } from '../services/messages';
import { Session, isTypeMessageUser, isTypeMessageSlot, isTypeMessageBot } from '../Types';
import { CalendarComponent } from './CalendarComponent';

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
    "intent_advisor_.*"
]

const ONE_WEEK_AGO = new Date();
ONE_WEEK_AGO.setDate(ONE_WEEK_AGO.getDate() - 6);

export const DashboardComponent = () => {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [filteredSessions, setFilteredSessions] = useState<Session[]>([]);

    // Stats
    const [sessionCounts, setSessionCounts] = useState<{ x: string; y: number; }[]>([]);
    const [intentCounts, setIntentCounts] = useState<{ [key: string]: number }>({});
    const [botMessageCount, setBotMessageCount] = useState(0);
    const [userMessageCount, setUserMessageCount] = useState(0);
    const [uniqueSenders, setUniqueSenders] = useState(0);
    const [totalConversations, setTotalConversations] = useState(0);
    const [thumbsUp, setThumbsUpCount] = useState(0);
    const [thumbsDown, setThumbsDownCount] = useState(0);

    // Filters
    const [startDate, setStartDate] = useState<Date>(ONE_WEEK_AGO); // starts at the beginning of the month
    const [endDate, setEndDate] = useState<Date>(new Date());
    const [toggleState, setToggleState] = useState<{internal: boolean, external: boolean, orgAdmins: boolean}>({ 
        internal: false,
        external: false,
        orgAdmins: false
    });

    const calculateCountsPerDay = useCallback(() => {
        const sessionCountByDay: { [key: string]: number } = {};

        filteredSessions.forEach((session) => {
            const day = new Date(session.timestamp * 1000).toISOString().split('T')[0];
            if (!sessionCountByDay[day]) {
                sessionCountByDay[day] = 0;
            }
            sessionCountByDay[day]++;
        });

        const sessionCountsArray = [];
        const currentDate = new Date(startDate);
        while (currentDate <= endDate) {
            const day = currentDate.toISOString().split('T')[0];
            sessionCountsArray.push({
                x: day.toString(),
                y: sessionCountByDay[day] || 0,
            });
            currentDate.setDate(currentDate.getDate() + 1);
        }

        setSessionCounts(sessionCountsArray);
    }, [filteredSessions, startDate, endDate]);

    // filter messages and calculate totals
    useEffect(() => {
        let thumbsUp = 0;
        let thumbsDown = 0;

        const filtered = sessions.filter((session) => {
            let internal = false;
            let orgAdmin = false;
            session.messages.filter(isTypeMessageUser).forEach((msg) => {
                if (msg.data.text === "/intent_core_session_start") {
                    orgAdmin = msg.data.metadata.is_org_admin;
                }
            });
            session.messages.filter(isTypeMessageSlot).forEach((msg) => {
                if (msg.data.name === 'is_internal') {
                    internal = msg.data.value === true ? true : false;
                }
            });

            if ((toggleState.internal && !internal) 
                || (toggleState.external && internal) 
                || (toggleState.orgAdmins && !orgAdmin))
            {
                return false;
            }
            return true;
        });

        setFilteredSessions(filtered);

        let botMessageCount = 0;
        let userMessageCount = 0;
        let conversationCount = 0;

        const intentCounts: { [key: string]: number } = {};

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
                    userMessageCount++;
                }
            });
        });

        setBotMessageCount(botMessageCount);
        setUserMessageCount(userMessageCount);
        setTotalConversations(conversationCount);

        setIntentCounts(intentCounts);

        const senders = new Set(filtered.map((session) => session.senderId));
        setUniqueSenders(senders.size);

        setThumbsUpCount(thumbsUp);
        setThumbsDownCount(thumbsDown);

        calculateCountsPerDay();
    }, [toggleState.internal, toggleState.external, toggleState.orgAdmins, sessions, calculateCountsPerDay]);

    useEffect(() => {
        const fetchMessages = async () => {
            const start = Math.floor(new Date(startDate.setHours(0,0,0,0)).getTime() / 1000);
            const end = Math.floor(endDate.getTime() / 1000);
    
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
                        <CardTitle>Filters</CardTitle>
                        <CardBody>
                            <Checkbox
                                label="Internal"
                                isChecked={toggleState.internal}
                                onChange={() => {
                                    setToggleState(prev => (
                                        {...prev, 
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
                                        {...prev, 
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
                                        {...prev, 
                                            orgAdmins: !prev.orgAdmins
                                        }
                                    ));
                                }}
                                id="toggle-org-admins"
                            />
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
                            title={Math.ceil((thumbsUp/(thumbsUp + thumbsDown)) * 100) + '%'}
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
                                <ListItem icon={<CheckCircleIcon />}>{Math.floor(((userMessageCount - intentCounts["nlu_fallback"]) / userMessageCount) * 100)}% Intents Recognized</ListItem>
                            </List>
                        </CardBody>
                    </Card>
                </GridItem>
                <GridItem span={4} rowSpan={4}>
                    <Card>
                        <CardTitle>{filteredSessions.length} Sessions</CardTitle>
                        <Chart
                            ariaTitle="Sessions over time"
                            containerComponent={<ChartVoronoiContainer labels={({ datum }) => `${datum.x}: ${datum.y}`} />}
                            name="usage"
                        >
                            {/* do not show dates */}
                            <ChartAxis tickValues={[]} /> 
                            <ChartAxis dependentAxis showGrid />
                            <ChartGroup>
                                <ChartLine
                                    data={sessionCounts}
                                    themeColor='purple'
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
                            <ChartAxis /> 
                            <ChartAxis dependentAxis showGrid />
                            <ChartGroup>
                                {Object.entries(intentCounts).map(([key, value]) => (
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
