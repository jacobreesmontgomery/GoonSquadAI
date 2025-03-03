import { useEffect, useState } from "react";
import axios from "axios";
import { Table } from "Components/Table";

export default function BasicStats() {
    const [headerStats, setHeaderStats] = useState<string[]>([]);
    const [rowData, setRowData] = useState<string[][]>([]);
    const [sortConfig, setSortConfig] = useState<{
        key: string;
        direction: "ascending" | "descending";
    } | null>(null);
    const [filters, setFilters] = useState<string[]>([]);

    useEffect(() => {
        axios
            .get("http://localhost:5001/api/activities/basic-stats")
            .then((response) => {
                setHeaderStats(response.data.headerStats);
                setRowData(response.data.rowData);
                setFilters(
                    new Array(response.data.headerStats.length).fill("")
                );
            })
            .catch((error) => {
                console.error("There was an error fetching the data!", error);
            });
    }, []);

    const handleSort = (key: string) => {
        let direction: "ascending" | "descending" = "ascending";
        if (
            sortConfig &&
            sortConfig.key === key &&
            sortConfig.direction === "ascending"
        ) {
            direction = "descending";
        }
        setSortConfig({ key, direction });
    };

    const handleFilterChange = (index: number, value: string) => {
        const newFilters = [...filters];
        newFilters[index] = value;
        setFilters(newFilters);
    };

    return (
        <div className="stats-container">
            <h2>Basic Stats</h2>
            <Table
                headers={headerStats}
                rowData={rowData}
                sortConfig={sortConfig}
                handleSort={handleSort}
                filters={filters}
                handleFilterChange={handleFilterChange}
            />
        </div>
    );
}
