import {
    CalendarMonth,
    List,
    ListItem,
    ListVariant,
    Card,
    CardTitle,
    CardBody
} from '@patternfly/react-core';

// dont allow dates older than 3 months
const OLDEST_ALLOWED_DATE = new Date();
OLDEST_ALLOWED_DATE.setMonth(OLDEST_ALLOWED_DATE.getMonth() - 3);

export const CalendarComponent = ({
    startDate,
    endDate,
    updateDateRange
}: {
    startDate: Date;
    endDate: Date;
    updateDateRange: (startDate: Date, endDate: Date) => void;
}) => {
    const handleDateChange = (date: Date) => {
        if (date > new Date()) {
            date = new Date(); // no future dates
        }
        if (date < OLDEST_ALLOWED_DATE) {
            date = OLDEST_ALLOWED_DATE; // no dates older than 3 months
        }

        if (date < startDate) {
            updateDateRange(date, endDate);
        } else if (date > endDate) {
            updateDateRange(startDate, date);
        } else {
            // If the selected date is between startDate and endDate, decide based on proximity
            const startDiff = Math.abs(date.getTime() - startDate.getTime());
            const endDiff = Math.abs(date.getTime() - endDate.getTime());
            if (startDiff < endDiff) {
                updateDateRange(date, endDate);
            } else {
                updateDateRange(startDate, date);
            }
        }
    };

    const handleDateChangeWithPresets = (preset: string) => {
        const newEndDate = new Date();
        const newStartDate = new Date();
        switch (preset) {
            case "1 week":
                newStartDate.setDate(newEndDate.getDate() - 6);
                break;
            case "1 month":
                newStartDate.setMonth(newEndDate.getMonth() - 1);
                break;
            case "3 months":
                newStartDate.setMonth(newEndDate.getMonth() - 3);
                break;
            default:
                return
        }
        updateDateRange(newStartDate, newEndDate);
    }

    return (
        <>
            <CalendarMonth
                date={endDate}
                onChange={(_event, date) => handleDateChange(date)}
                onMonthChange={() => {}}
                rangeStart={startDate}
            />
            <Card>
                <CardTitle>Presets</CardTitle>
                <CardBody>
                    <List variant={ListVariant.inline}>
                        <ListItem className="pf-v5-c-button pf-m-link pf-m-inline" onClick={() => handleDateChangeWithPresets("1 week")}>1 week</ListItem>
                        <ListItem className="pf-v5-c-button pf-m-link pf-m-inline" onClick={() => handleDateChangeWithPresets("1 month")}>1 month</ListItem>
                        <ListItem className="pf-v5-c-button pf-m-link pf-m-inline" onClick={() => handleDateChangeWithPresets("3 months")}>3 months</ListItem>
                    </List>
                </CardBody>
            </Card>
        </>
    );
};