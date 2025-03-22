import { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { Table } from "Components/Table";
import "../App/App.css";
import styled from "styled-components";

const SectionHeader = styled.h2`
    color: ${(props) => props.theme.headerText};
    margin-bottom: 1.5rem;
`;

const StatsContainer = styled.div`
    background-color: ${(props) => props.theme.cardBackground};
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: ${(props) => props.theme.shadow};
    border: 1px solid ${(props) => props.theme.containerBorder};
    height: 100vh;
`;

const ATHLETE_DATA_FIELDNAMES = [
    "ATHLETE",
    "ACTIVITY ID",
    "RUN",
    "MOVING TIME",
    "DISTANCE (MI)",
    "PACE (MIN/MI)",
    "FULL DATE",
    "TIME",
    "DAY",
    "MONTH",
    "DATE",
    "YEAR",
    "SPM AVG",
    "HR AVG",
    "WKT TYPE",
    "DESCRIPTION",
    "TOTAL ELEV GAIN (FT)",
    "MANUAL",
    "MAX SPEED (FT/S)",
    "CALORIES",
    "ACHIEVEMENT COUNT",
    "KUDOS COUNT",
    "COMMENT COUNT",
    "ATHLETE COUNT",
    "FULL DATETIME",
];
const MAPPED_FIELDNAMES = {
    athlete_id: ATHLETE_DATA_FIELDNAMES[0],
    activity_id: ATHLETE_DATA_FIELDNAMES[1],
    run: ATHLETE_DATA_FIELDNAMES[2],
    moving_time: ATHLETE_DATA_FIELDNAMES[3],
    distance_mi: ATHLETE_DATA_FIELDNAMES[4],
    pace_min_mi: ATHLETE_DATA_FIELDNAMES[5],
    full_date: ATHLETE_DATA_FIELDNAMES[6],
    time: ATHLETE_DATA_FIELDNAMES[7],
    day: ATHLETE_DATA_FIELDNAMES[8],
    month: ATHLETE_DATA_FIELDNAMES[9],
    date: ATHLETE_DATA_FIELDNAMES[10],
    year: ATHLETE_DATA_FIELDNAMES[11],
    spm_avg: ATHLETE_DATA_FIELDNAMES[12],
    hr_avg: ATHLETE_DATA_FIELDNAMES[13],
    wkt_type: ATHLETE_DATA_FIELDNAMES[14],
    description: ATHLETE_DATA_FIELDNAMES[15],
    total_elev_gain_ft: ATHLETE_DATA_FIELDNAMES[16],
    manual: ATHLETE_DATA_FIELDNAMES[17],
    max_speed_ft_s: ATHLETE_DATA_FIELDNAMES[18],
    calories: ATHLETE_DATA_FIELDNAMES[19],
    achievement_count: ATHLETE_DATA_FIELDNAMES[20],
    kudos_count: ATHLETE_DATA_FIELDNAMES[21],
    comment_count: ATHLETE_DATA_FIELDNAMES[22],
    athlete_count: ATHLETE_DATA_FIELDNAMES[23],
    full_datetime: ATHLETE_DATA_FIELDNAMES[24],
};
const ATHLETE_DATA_FILTERED_FIELDNAMES = [
    ATHLETE_DATA_FIELDNAMES[0], // "ATHLETE"
    ATHLETE_DATA_FIELDNAMES[2], // "RUN"
    ATHLETE_DATA_FIELDNAMES[3], // "MOVING TIME"
    ATHLETE_DATA_FIELDNAMES[4], // "DISTANCE (MI)"
    ATHLETE_DATA_FIELDNAMES[5], // "PACE (MIN/MI)"
    ATHLETE_DATA_FIELDNAMES[12], // "SPM AVG"
    ATHLETE_DATA_FIELDNAMES[13], // "HR AVG"
    ATHLETE_DATA_FIELDNAMES[14], // "WKT TYPE"
    ATHLETE_DATA_FIELDNAMES[15], // "DESCRIPTION"
    ATHLETE_DATA_FIELDNAMES[16], // "TOTAL ELEV GAIN (FT)"
    ATHLETE_DATA_FIELDNAMES[24], // "FULL DATETIME"
];

export default function Database() {
    const [headerStats, setHeaderStats] = useState<string[]>([]);
    const [rowData, setRowData] = useState<string[][]>([]);
    const [sortConfig, setSortConfig] = useState<{
        key: string;
        direction: "ascending" | "descending";
    } | null>(null);
    const [filters, setFilters] = useState<string[]>([]);

    const filterHeaderStats = useCallback((headerStats: string[]) => {
        return headerStats.filter((header) =>
            Object.keys(MAPPED_FIELDNAMES).includes(header)
        );
    }, []);

    /**
     * Filter out the columns from each record that we don't want to display in the table.
     * @param rowData The data to filter.
     * @returns The filtered data.
     */
    const filterRowData = useCallback((rowData: Record<string, any>[]) => {
        return rowData.map((row) =>
            ATHLETE_DATA_FILTERED_FIELDNAMES.map((field) => row[field])
        );
    }, []);

    useEffect(() => {
        axios
            .get("http://localhost:5001/api/activities/detailed-stats")
            .then((response) => {
                const headersStats = filterHeaderStats(
                    response.data.data.headers
                );
                const rowData = filterRowData(response.data.data.activities);
                setHeaderStats(headersStats);
                setRowData(rowData);
                setFilters(
                    new Array(response.data.data.headers.length).fill("")
                );
            })
            .catch((error) => {
                console.error("There was an error fetching the data!", error);
            });
    }, [filterHeaderStats, filterRowData]);

    const handleSort = useCallback(
        (key: string) => {
            let direction: "ascending" | "descending" = "ascending";
            if (
                sortConfig &&
                sortConfig.key === key &&
                sortConfig.direction === "ascending"
            ) {
                direction = "descending";
            }
            setSortConfig({ key, direction });
        },
        [sortConfig]
    );

    const handleFilterChange = useCallback(
        (index: number, value: string) => {
            const newFilters = [...filters];
            newFilters[index] = value;
            setFilters(newFilters);
        },
        [filters]
    );

    return (
        <StatsContainer>
            <SectionHeader>Database</SectionHeader>
            <Table
                headers={headerStats}
                rowData={rowData}
                sortConfig={sortConfig}
                handleSort={handleSort}
                filters={filters}
                handleFilterChange={handleFilterChange}
            />
        </StatsContainer>
    );
}
