import { useCallback, useEffect, useState } from 'react';
import {
  CalendarMonth,
  Checkbox,
  Card,
  Grid,
  GridItem,
  PageSectionVariants,
  PageSection,
} from '@patternfly/react-core';
import {
  ChartDonut,
  ChartPie,
  ChartArea,
  Chart,
  ChartVoronoiContainer,
  ChartAxis,
  ChartGroup,

} from '@patternfly/react-charts';
import { getSessionsInRange } from '../services/messages';
import { Session, isTypeMessageUser, isTypeMessageSlot, isTypeMessageBot } from '../Types';

export const DashboardComponent = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [filteredSessions, setFilteredSessions] = useState<Session[]>([]);
  const [sessionCounts, setSessionCounts] = useState<{ x: string; y: number; }[]>([]);
  const [uniqueSenders, setUniqueSenders] = useState(0);
  const [totalConversations, setTotalConversations] = useState(0);
  const [thumbsUp, setThumbsUpCount] = useState(0);
  const [thumbsDown, setThumbsDownCount] = useState(0);

  // Filters
  // starting date at the beginning of the month
  const [startDate, setStartDate] = useState<Date>(new Date(new Date().setDate(1)));
  const [endDate, setEndDate] = useState<Date>(new Date());
  const [toggleState, setToggleState] = useState({ 
    internal: true,
    external: true,
    orgAdmins: false
  });

  // filter messages and calculate totals
  useEffect(() => {
    console.log('callback')
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

      if (toggleState.internal && internal) {
        return true;
      } else if (toggleState.external && !internal) {
        return true;
      } else if (toggleState.orgAdmins && orgAdmin) {
        return true;
      } 
      return false;
    });

    setFilteredSessions(filtered);

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
        }
      });
    });

    const senders = new Set(filtered.map((session) => session.senderId));
    setUniqueSenders(senders.size);

    setThumbsUpCount(thumbsUp);
    setThumbsDownCount(thumbsDown);
  }, [toggleState, sessions]);

  useEffect(() => {
    console.log('useEffect')
    const fetchMessages = async () => {
      const start = Math.floor(new Date(startDate.setHours(0,0,0,0)).getTime() / 1000);
      const end = Math.floor(endDate.getTime() / 1000);

      console.log(`Fetching messages from ${start} to ${end}`);
  
      const sessionsInRange = await getSessionsInRange(undefined, start, end);
      setSessions(sessionsInRange);
    };
    fetchMessages();
  }, [startDate, endDate]);

  const calculateSessionsPerDay = useCallback(() => {
    const sessionCountByDay: { [key: string]: number } = {};

    sessions.forEach((session) => {
      const day = new Date(session.timestamp * 1000).toISOString().split('T')[0];
      console.log(day);
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
  }, [sessions, startDate, endDate]);

  useEffect(() => {
    calculateSessionsPerDay();
  }, [calculateSessionsPerDay]);

  const handleDateChange = (date: Date) => {
    console.log('handle date')
    if (date < endDate) {
      setStartDate(date);
    } else {
      setEndDate(date);
    }
  };

  const handleToggle = (toggleName:  'showInternal' | 'showExternal' | 'showOrgAdmins') => {
    console.log('handle toggle')
    const newToggleState = toggleState;

    console.log(`Toggling ${toggleName}`);

    if (toggleName === 'showInternal'){
      newToggleState.internal = !toggleState.internal;
    } else if(toggleName === 'showExternal'){
      newToggleState.external = !toggleState.external;
    } else if(toggleName === 'showOrgAdmins'){
      newToggleState.orgAdmins = !toggleState.orgAdmins;
    }

    console.log(newToggleState);
    setToggleState(newToggleState);
  };

  const tickIndex = [
    0, // First date
    Math.floor(sessionCounts.length / 2), // Median date
    sessionCounts.length - 1 // Last date
  ];
  const tickLabels = tickIndex.map(index => sessionCounts[index]?.x);

  return (
    <PageSection variant={PageSectionVariants.light}>
      <Grid hasGutter>
        <GridItem span={3} rowSpan={2}>
          <CalendarMonth
            date={endDate}
            onChange={(_event, date) => handleDateChange(date)}
            onMonthChange={() => {}}
            rangeStart={startDate}
          />
          <div>
            <b> User Type </b>
            <Checkbox
              label="Internal"
              isChecked={toggleState.internal}
              onChange={() => handleToggle('showInternal')}
              id="toggle-internal"
            />
            <Checkbox
              label="External"
              isChecked={toggleState.external}
              onChange={() => handleToggle('showExternal')}
              id="toggle-external"
            />
            <Checkbox
              label="Org Admins Only"
              isChecked={toggleState.orgAdmins}
              onChange={() => handleToggle('showOrgAdmins')}
              id="toggle-org-admins"
            />
          </div>
        </GridItem>
        <GridItem span={2} rowSpan={1}>
          <Card component="div">
            <ChartDonut
              data={[
                { x: 'Up', y: thumbsUp },
                { x: 'Down', y: thumbsDown }
              ]}
              title="Feedback"
              subTitle="Thumbs Up vs Down"
              constrainToVisibleArea
              labels={({ datum }) => `${datum.x}: ${datum.y}`}
              legendPosition="bottom"
              themeColor='cyan'
              legendData={[
                { name: `Thumbs Up: ${thumbsUp}` },
                { name: `Thumbs Down: ${thumbsDown}` }
              ]}
              padding={{
                bottom: 50
              }}
            />
          </Card>
        </GridItem>
        <GridItem span={2} rowSpan={1}>
          <Card component="div">
            <ChartPie
              data={[
                { x: 'Unique Sessions', y: filteredSessions.length },
                { x: 'Total Conversations', y: totalConversations }
              ]}
              constrainToVisibleArea
              themeColor='multi'
              labels={({ datum }) => `${datum.x}: ${datum.y}`}
              legendPosition="bottom"
              legendData={[
                { name: `Unique Sessions: ${thumbsUp}` },
                { name: `Total Sessions: ${thumbsDown}` }
              ]}
            />
          </Card>
        </GridItem>
        <GridItem span={3}>
          <Chart
            ariaDesc="Usage over time"
            ariaTitle="User messages over time"
            containerComponent={<ChartVoronoiContainer labels={({ datum }) => `${datum.x}: ${datum.y}`} constrainToVisibleArea />}
            name="usage"
          >
            <ChartAxis tickValues={[]} />
            <ChartAxis dependentAxis showGrid />
            <ChartGroup>
              <ChartArea
                data={sessionCounts}
                themeColor='purple'
                interpolation="monotoneX"
              />
            </ChartGroup>
          </Chart>
        </GridItem>
        {/* <GridItem span={3}>
          <ChartArea
            data={[{
              name: 'Unique Users',
              data: sessions.map((sess, idx) => ({ x: sess.timestamp, y: uniqueSenders }))
            }]}
            themeColor='blue'
          />
        </GridItem> */}
      </Grid>
    </PageSection>
  );
};
