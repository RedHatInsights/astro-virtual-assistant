import { useEffect, useState } from 'react';
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

} from '@patternfly/react-charts';
import { getMessagesInRange } from '../services/messages';
import { Message } from '../Types';


export const DashboardComponent = () => {
  const [startDate, setStartDate] = useState<Date | null>(null);
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
    <Card style={{ width: '100vw', height: '200vh', display: 'flex', flexDirection: 'column', paddingTop: '5px' }}> 
      <Grid hasGutter>
        <GridItem span={12} style={{ textAlign: 'center', marginBottom: '5px' }}> 
          <CalendarMonth
            date={startDate || endDate || new Date()}
            onChange={(_event, date) => handleDateChange(date)}
            onMonthChange={() => {}}
            style={{ width: '50%', justifyContent: 'center'}} 
          />
          {startDate && endDate && (
            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px'}}>
              Selected Date Range: {startDate.toLocaleString()} - {endDate.toLocaleString()}
            </div>
          )}
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
          </div>
          <div style={{display: 'flex', justifyContent: 'center', gap: '8rem'}}>
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
          </GridItem>
        </Grid>
        
      <div style={{ flexGrow: 1, padding: '0 10px' }}>
        <Grid hasGutter style={{ marginTop: '50px'}}>
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
                { x: 'Total Conversations', y: totalConversations }
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
          <GridItem span={6} style={{ marginTop: '50px'}}>
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
          <GridItem span={6} style={{ marginTop: '50px'}}>
            <h4 style={{ textAlign: 'center' }}>Unique Users</h4>
            <ChartArea
              data={[{
                name: 'Unique Users',
                data: messages.map((_, idx) => ({ x: idx, y: uniqueSenders }))
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
