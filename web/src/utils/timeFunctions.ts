import { useMemo } from "react";

export function useTimeFilterDates(timeFilter: string): { startDate: string, endDate: string } {
    return useMemo(() => {
        const endDate = new Date();
        const startDate = new Date();
        switch (timeFilter) {
            case '12months':
                startDate.setMonth(endDate.getMonth() - 12);
                break;
            case '6months':
                startDate.setMonth(endDate.getMonth() - 6);
                break;
            case '1month':
                startDate.setMonth(endDate.getMonth() - 1);
                break;
            case '14days':
                startDate.setDate(endDate.getDate() - 14);
                break;
        }
        return {
            startDate: startDate.toISOString().split('T')[0],
            endDate: endDate.toISOString().split('T')[0]
        };
    }, [timeFilter]);
}