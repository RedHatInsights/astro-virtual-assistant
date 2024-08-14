import { CalendarMonth } from '@patternfly/react-core/dist/esm/components/CalendarMonth/CalendarMonth';

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

    return (
        <CalendarMonth
            date={endDate}
            onChange={(_event, date) => handleDateChange(date)}
            onMonthChange={() => {}}
            rangeStart={startDate}
        />
    );
};