import React, { useEffect, useState } from 'react';
import {
  CalendarMonth,
  Checkbox,
  Card,
  Grid,
  GridItem,
} from '@patternfly/react-core';
import {
  ChartDonut,
  ChartPie,
  ChartArea,
  ChartScatter,
  ChartThemeColor,
  ChartVoronoiContainer,
  ChartBar
} from '@patternfly/react-charts';
import { getMessagesInRange } from '../services/messages';
import { Message } from '../Types';

export const DashboardComponent = () => {
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [uniqueSessionsCount, setUniqueSessionsCount] = useState(10);
  const [uniqueSenders, setUniqueSenders] =useState(10);
  const [totalSessions, setTotalSessions] = useState(60);
  const [averageFlows, setAverageFlows] = useState(1000);
  const [thumbsUp, setThumbsUpCount] = useState(50);
  const [thumbsDown, setThumbsDownCount] = useState(40);
  const [toggleState, setToggleState] = useState({
    showAll: true,  
    showInternal: false,
    showExternal: false
  });

  useEffect(() => {
    if (startDate && endDate) {
      const fetchMessages = async () => {
        const sessionMessages = await getMessagesInRange(undefined, Math.floor(startDate.getTime() / 1000), Math.floor(endDate.getTime() / 1000));
        setMessages(sessionMessages);
      };
      fetchMessages();
    }
    setTotalSessions(messages.length)
    
    const uniqueSessions =new Set(messages.map(msg => msg.id)).size;
    setUniqueSessionsCount(uniqueSessions);

    const uniqueSenders = new Set(messages.map(msg =>msg.sender_id)).size;
    setUniqueSenders(uniqueSenders);

    function isSlotMessage(msg: Message): boolean {
      return msg.type_name === 'slot' && msg.data.name === 'closing_feedback';
    }
    
    const thumbsUp = messages.filter(msg => isSlotMessage(msg)).length;
    const thumbsDown = messages.filter(msg => !isSlotMessage(msg)).length; 
    setThumbsUpCount(thumbsUp); 
    setThumbsDownCount(thumbsDown);
 

    const totalConversations = messages.reduce((acc,msg) => acc + msg.id, 0);
    const averageConversations = messages.length > 0 ? (totalConversations / messages.length) : 0;
    setAverageFlows(averageConversations);
    setTotalSessions(messages.length)

  }, [startDate, endDate,messages]);

  const handleDateChange = (date: Date) => {
    if (!startDate || (startDate && endDate)) {
      setStartDate(date);
      setEndDate(date);
    } else if (startDate && !endDate) {
      if (date >= startDate) {
        setEndDate(date);
      } else {
        setStartDate(date);
      }
    }
  };

  const rangeString = startDate && endDate
    ? `${startDate.toLocaleDateString()} TO ${endDate.toLocaleDateString()}`
    : startDate
      ? `${startDate.toLocaleDateString()} TO (end date not selected)`
      : endDate
        ? `(start date not selected) TO ${endDate.toLocaleDateString()}`
        : 'No date selected';
  
  const handleToggle = (toggleName: 'showAll' | 'showInternal' | 'showExternal') => {
  const newToggleState = {
    showAll: false,
    showInternal: false,
    showExternal: false,
  }; 

  if (toggleName === 'showAll') {
    newToggleState.showInternal= true;
    newToggleState.showExternal= true;
  } else {
   if(toggleName === 'showInternal'){
    newToggleState.showInternal= true;
    newToggleState.showExternal= false;
  }else if(toggleName === 'showExternal'){
    newToggleState.showExternal= true;
    newToggleState.showInternal= false;
  }}
  setToggleState(newToggleState);

  const isInternalMessage = (messages : any) => {
    return messages.data && typeof messages.data.name === 'string' && messages.data.name === 'is_internal';
  };

  const isExternalMessage = (messages : any) => {
    return messages.data && typeof messages.data.name === 'string' && messages.data.name !== 'is_internal';
  };

  const filteredMessages = messages.filter(messages =>
    toggleState.showAll ||
    (toggleState.showInternal && isInternalMessage(messages)) ||
    (toggleState.showExternal && isExternalMessage(messages))
  );
}

  return (
    <Card style={{ width: '100vw', height: '200vh', display: 'flex', flexDirection: 'column', paddingTop: '5px' }}> 
      <Grid hasGutter>
        <GridItem span={12} style={{ textAlign: 'center', marginBottom: '5px' }}> 
          <CalendarMonth
            date={startDate && endDate|| new Date()}
            onChange={(event, date) => handleDateChange(date)}
            onMonthChange={() => {}}
            style={{ width: '50%', justifyContent: 'center'}} 
          />
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <div style={{ textAlign: 'center', margin: '20px 0' }}>{rangeString}</div>
          </div>
          <div style={{display: 'flex', justifyContent: 'center', gap: '8rem'}}>
          <b> User Type </b>
          <Checkbox
            label="Show All"
            isChecked={toggleState.showAll}
            onChange={() => handleToggle('showAll')} 
            id="toggle-all"
          />
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
          </GridItem>
        </Grid>
        
      <div style={{ flexGrow: 1, padding: '0 10px' }}>
        <Grid hasGutter style={{ marginTop: '60px'}}>
          <GridItem span={6}>
            <b><h1 style={{ textAlign: 'center' }}>Feedback</h1></b>
            <ChartDonut
              data={[
                { x: 'Thumbs Up', y: thumbsUp },
                { x: 'Thumbs Down', y: thumbsDown }
              ]}
              title="Feedback"
              subTitle="Thumbs Up vs Down"
              height={200}
              width={300}
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
          </GridItem>
          <GridItem span={6}>
            <h4 style={{ textAlign: 'center' }}>Session Statistics</h4>
            <ChartPie
              data={[
                { x: 'Unique Sessions', y: uniqueSessionsCount },
                { x: 'Total Sessions', y: totalSessions }
              ]}
              height={200}
              width={300}
              constrainToVisibleArea
              themeColor='multi'
              labels={({ datum }) => `${datum.x}: ${datum.y}`}
              legendPosition="bottom"
              legendData={[
                { name: `Unique Sessions: ${thumbsUp}` },
                { name: `Total Sessions: ${thumbsDown}` }
              ]}
              padding={{
                bottom: 50
              }}
            />
          </GridItem>
          <GridItem span={6}>
            <h4 style={{ textAlign: 'center' }}>Conversations</h4>
            <ChartBar
              data={[
                { x: 'Average Conversations', y: averageFlows },
                { x: 'Total Conversations', y: totalSessions }
              ]}
              height={200}
              width={700}
              themeColor='multi'
              containerComponent={<ChartVoronoiContainer labels={({ datum }) => `${datum.name}: ${datum.y}`} constrainToVisibleArea />}
              padding={{
                bottom: 50
              }}
            />
          </GridItem>
          <GridItem span={6}>
            <h4 style={{ textAlign: 'center' }}>Usage Over Time</h4>
            <ChartArea
              data={[{
                name: 'Usage Over Time',
                data: messages.map((msg, idx) => ({ x: idx, y: msg.id }))
              }]}
              themeColor='purple'
              height={200}
              width={300}
              labels={({ datum }) => `${datum.x}: ${datum.y}`}
            />
          </GridItem>
          <GridItem span={6}>
            <h4 style={{ textAlign: 'center' }}>Unique Users</h4>
            <ChartScatter
              data={[{
                name: 'Unique Users',
                data: messages.map((messages, idx) => ({ x: idx, y: uniqueSenders }))
              }]}
              height={200}
              width={300}
              themeColor='blue'
            />
          </GridItem>
        </Grid>
      </div>
    </Card>
  );
};
