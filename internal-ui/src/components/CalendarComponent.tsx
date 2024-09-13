import { useEffect, useState } from 'react';
import {
    CalendarMonth,
    List,
    ListItem,
    ListVariant,
    Card,
    CardTitle,
    CardBody
} from '@patternfly/react-core';
import { SimpleSelect, SimpleSelectOption } from '@patternfly/react-templates';

export const CalendarComponent = ({
    startDate,
    endDate,
    updateDateRange
}: {
    startDate: Date;
    endDate: Date;
    updateDateRange: (startDate: Date, endDate: Date) => void;
}) => {
    const [selectedMonth, setSelectedMonth] = useState<string>('');
    const [selectedYear, setSelectedYear] = useState<string>('');
    const [monthOptions, setMonthOptions] = useState<SimpleSelectOption[]>([]);
    const [yearOptions, setYearOptions] = useState<SimpleSelectOption[]>([]);

    useEffect(() => {
        const calculateMonthsAndYears = () => {
            const today = new Date();
            const pastDate = new Date();
            pastDate.setDate(today.getDate() - 180);

            const months = new Set<string>();
            const years = new Set<string>();

            for (let d = new Date(pastDate); d <= today; d.setMonth(d.getMonth() + 1)) {
                months.add(d.toLocaleString('default', { month: 'long' }));
                years.add(d.getFullYear().toString());
            }

            setMonthOptions(Array.from(months).map(month => ({ content: month, value: month })));
            setYearOptions(Array.from(years).map(year => ({ content: year, value: year })));
        };

        calculateMonthsAndYears();
    }, []);

    const handleDateChange = (date: Date) => {
        if (date > new Date()) {
            date = new Date(); // no future dates
        }

        let start = startDate;
        let end = endDate;

        // If the selected date is between startDate and endDate, decide based on proximity
        const startDiff = Math.abs(date.getTime() - startDate.getTime());
        const endDiff = Math.abs(date.getTime() - endDate.getTime());
        if (startDiff < endDiff) {
            start = date;
        } else {
            end = date;
        }

        // ensure that the start date and end date are not more than 3 months apart
        const three_months = 1000 * 60 * 60 * 24 * 30 * 3;
        const rangeDiff = Math.abs(end.getTime() - start.getTime());
        if (rangeDiff > three_months) {
            end = new Date(start.getTime() + three_months);
        }

        updateDateRange(start, end);
        setSelectedMonth('');
        setSelectedYear('');
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
        setSelectedMonth('');
        setSelectedYear('');
    }

    const handleMonthSelect = (selection: string | number) => {
        if (typeof selection === 'number') {
            return;
        }
        setSelectedMonth(selection);
        updateDateBasedOnMonth(selection, selectedYear);
    }
    
    const handleYearSelect = (selection: string | number) => {
        if (typeof selection === 'number') {
            return;
        }
        setSelectedYear(selection);
        updateDateBasedOnMonth(selectedMonth, selection);
    }

    const updateDateBasedOnMonth = (month: string, year: string) => {
        if (!(month && year)) {
            return;
        }

        const start = new Date(`${month} 1, ${year}`);
        const end = new Date(start);
        end.setMonth(end.getMonth() + 1);
        end.setDate(end.getDate() - 1);

        updateDateRange(start, end);
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
                    <br />By month:<br />
                    <SimpleSelect
                        initialOptions={monthOptions}
                        onSelect={(_ev, selection) => handleMonthSelect(selection)}
                    />
                    <SimpleSelect
                        initialOptions={yearOptions}
                        onSelect={(_ev, selection) => handleYearSelect(selection)}
                    />
                </CardBody>
            </Card>
        </>
    );
};