import { useEffect, useState } from 'react';
import {
  CalendarMonth,
  Checkbox,
  Card,
  Grid,
  GridItem,
  PageSectionVariants,
  PageSection,
  Split,
  SplitItem,
} from '@patternfly/react-core';
import {
  ChartDonut,
  ChartPie,
  ChartArea,

} from '@patternfly/react-charts';
import { getMessagesInRange } from '../services/messages';
import { Message } from '../Types';


export const DashboardComponent = () => {
  const [startDate, setStartDate] = useState<Date>(new Date());
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [uniqueSessionsCount, setUniqueSessionsCount] = useState(0);
  const [uniqueSenders, setUniqueSenders] =useState(0);
  const [totalConversations, setTotalConversations] = useState(0);
  const [thumbsUp, setThumbsUpCount] = useState(0);
  const [thumbsDown, setThumbsDownCount] = useState(0);
  const [toggleState, setToggleState] = useState({ 
    showInternal: false,
    showExternal: false
  });

  useEffect(() => {
    const fetchMessages = async () => {
      if (startDate && endDate) {
          const currentDay = new Date().toDateString();
          const adjustedEndDate = new Date(endDate);
  
          if (adjustedEndDate.toDateString() === currentDay) {
            adjustedEndDate.setTime(Date.now()); 
          } else {
            adjustedEndDate.setHours(23, 59, 59, 999); 
          }
  
        const sessionMessages = await getMessagesInRange(undefined, Math.floor(startDate.getTime() / 1000), Math.floor(adjustedEndDate.getTime() / 1000));
        setMessages(sessionMessages);
        const uniqueSessions = new Set(sessionMessages.map(msg => msg.id)).size;
        const uniqueSenders = new Set(sessionMessages.map(msg => msg.sender_id)).size;
        const totalConversations = sessionMessages.length;

        let thumbsUpCount = 0;
        let thumbsDownCount = 0;
        

        sessionMessages.forEach((msg) => {
          if (msg.type_name === 'slot' && msg.data.name === 'closing_feedback') {
            thumbsUpCount++;
          } else {
            thumbsDownCount++;
          }
        });
        setUniqueSessionsCount(uniqueSessions);
        setUniqueSenders(uniqueSenders);
        setThumbsUpCount(thumbsUpCount);
        setThumbsDownCount(thumbsDownCount);
        setTotalConversations(totalConversations);
      }
    };

    fetchMessages();
  }, [startDate, endDate]);

  const handleDateChange = (date: Date) => {
    if (!startDate || (startDate && endDate)) {
      setStartDate(date);
      setEndDate(null);
    } else if (startDate && !endDate) {
      if (date >= startDate) {
        setEndDate(date);
      } else {
        setStartDate(date);
      }
    }
  };

  const handleToggle = (toggleName:  'showInternal' | 'showExternal') => {
  const newToggleState = {
    showInternal: false,
    showExternal: false,
  }; 

  const isInternalMessage = (messages : any) => {
    return messages.data && typeof messages.data.name === 'string' && messages.data.name === 'is_internal';
  };

  const isExternalMessage = (messages : any) => {
    return messages.data && typeof messages.data.name === 'string' && messages.data.name !== 'is_internal';
  };

   if(toggleName === 'showInternal'){
    newToggleState.showInternal= true;
    newToggleState.showExternal= false;
    let filteredMessages = messages.filter (messages => (toggleState.showInternal && isInternalMessage(messages)))
    setMessages(filteredMessages);

  }else if(toggleName === 'showExternal'){
    newToggleState.showExternal= true;
    newToggleState.showInternal= false;
    let filteredMessages = messages.filter (messages =>  (toggleState.showExternal && isExternalMessage(messages)))
    setMessages(filteredMessages);
  }
  setToggleState(newToggleState);
}

  return (
    <PageSection variant={PageSectionVariants.light}>
      <Split hasGutter>
        <SplitItem>
          <CalendarMonth
            date={endDate || startDate}
            onChange={(_event, date) => handleDateChange(date)}
            onMonthChange={() => {}}
            rangeStart={startDate}
          />
          <div>
            <b> User Type </b>
            <Checkbox
              label="Show Internal"
              isChecked={toggleState.showInternal}
              onChange={() => handleToggle('showInternal')}
              id="toggle-internal"
            />
            <Checkbox
              label="Show External"
              isChecked={toggleState.showExternal}
              onChange={() => handleToggle('showExternal')}
              id="toggle-external"
            />
          </div>
        </SplitItem>
        <SplitItem isFilled>
          <Grid hasGutter style={{ marginTop: '50px'}}>
            <GridItem span={1} rowSpan={1}>
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
            <GridItem span={1} rowSpan={1}>
              <Card component="div">
                <ChartPie
                  data={[
                    { x: 'Unique Sessions', y: uniqueSessionsCount },
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
            <GridItem span={2}>
              <ChartArea
                data={[{
                  name: 'Usage Over Time',
                  data: messages.map((msg, idx) => ({ x: idx, y: msg.id }))
                }]}
                themeColor='purple'
                labels={({ datum }) => `${datum.x}: ${datum.y}`}
              />
            </GridItem>
            <GridItem span={2} style={{ marginTop: '50px'}}>
              <ChartArea
                data={[{
                  name: 'Unique Users',
                  data: messages.map((_, idx) => ({ x: idx, y: uniqueSenders }))
                }]}
                themeColor='blue'
              />
            </GridItem>
          </Grid>
        </SplitItem>
      </Split>
    </PageSection>
  );
};
