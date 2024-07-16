import React from 'react';
import { CalendarMonth } from '@patternfly/react-core';
import { Checkbox } from '@patternfly/react-core';
import {
  Card,
  CardBody,
  CardTitle,
  CardHeader,
} from '@patternfly/react-core';
import { useState } from 'react';


export const SelectFilters = () => {
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);

  const handleDateChange = (_event: React.MouseEvent<HTMLButtonElement, MouseEvent>, date: Date) => {
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

  const rangeString = startDate && endDate
    ? `${startDate.toLocaleDateString()} TO ${endDate.toLocaleDateString()}`
    : startDate
    ? `${startDate.toLocaleDateString()} TO (end date not selected)`
    : endDate
    ? `(start date not selected) TO ${endDate.toLocaleDateString()}`
    : 'No date selected';

  return (
    <Card style={{ width: '500px', height: '650px' }} >
      <CardTitle> Filters for Visualization</CardTitle>
      <CardHeader>
       Pick the Time Frame for Inference
      </CardHeader>
      <CardBody style={{alignItems: 'center'}}>
      <div className="calendar-container" style={{alignItems: 'center'}}>
        <CalendarMonth
          date={startDate || new Date()}
          onChange={handleDateChange}
          onMonthChange={() => {}}
        />
        </div>
        <pre style={{alignItems: 'center', margin:'0 auto',maxWidth: '100%'}}>Date Range: {rangeString}</pre>
      </CardBody>
      <CardHeader>
          <CardTitle>Select the Type of User</CardTitle>
        </CardHeader>
        <CardBody>
          <Checkbox
            label="Internal"
            id="internal-checkbox"
          />
          <Checkbox
            label="External"
            id="external-checkbox"
          />
           <Checkbox
            label="Org Admin"
            id="org-admin-checkbox"
          />
          <Checkbox
            label="Non-Org Admin"
            id="non-org-admin-checkbox"
          />
        </CardBody>
    </Card>
  );
};


  export const NumberOfSessions= () =>  {
    return (
      <Card style={{ width: '900px', height: '150px'}}>
        <CardHeader>
          <CardTitle>Number of Sessions</CardTitle>
        </CardHeader>
        <CardBody>
        </CardBody>
      </Card>
    );
  };

  export const SessionReviewCount= () =>  {
    return (
      <Card style={{ width: '900px', height: '150px'}}>
        <CardHeader>
          <CardTitle>Thumbs Up/ Thumbs Down Statistics</CardTitle>
        </CardHeader>
        <CardBody>
        </CardBody>
      </Card>
    );
  };

  export const AverageNumberofConversations= () =>  {
    return (
      <Card style={{ width: '900px', height: '150px'}}>
        <CardHeader>
          <CardTitle>Average Number of Conversations</CardTitle>
        </CardHeader>
        <CardBody>
        </CardBody>
      </Card>
    );
  };

  export const UniqueUsers= () =>  {
    return (
      <Card style={{ width: '900px', height: '150px'}}>
        <CardHeader>
          <CardTitle>Number of Unique Users</CardTitle>
        </CardHeader>
        <CardBody>
        </CardBody>
      </Card>
    );
  };

  export const AverageUserStatistics= () =>  {
    return (
      <Card style={{ width: '900px', height: '150px'}}>
        <CardHeader>
          <CardTitle>Average User Statistics</CardTitle>
        </CardHeader>
        <CardBody>
        </CardBody>
      </Card>
    );
  };

 