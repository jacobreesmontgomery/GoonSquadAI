import styled from "styled-components";
import { AuthButton } from "Components/AuthButton";

const HomeContainer = styled.div`
    background-color: ${(props) => props.theme.homeContainer};
    border: 0.0625rem solid ${(props) => props.theme.homeContainerBorder};
    padding: ${(props) => props.theme.contentPadding};
    max-width: 100%;
    width: 100%;
    height: 100%;
    box-shadow: ${(props) => props.theme.shadow};
    box-sizing: border-box;
`;

const Content = styled.div`
    font-size: 1.1rem;
    line-height: 1.6;
    color: ${(props) => props.theme.text};
    max-width: 100%;
`;

const TableContainer = styled.div`
    width: 100%;
    overflow-x: auto;
    margin-top: 1.25rem;
`;

const Table = styled.table`
    border-collapse: collapse;
    border: 0.0625rem solid ${(props) => props.theme.tableBorder};
    box-shadow: ${(props) => props.theme.tableShadow};
    border-radius: 0.25rem;
    width: 100%;
`;

const TableHeader = styled.th`
    background-color: ${(props) => props.theme.tableHeader};
    color: ${(props) => props.theme.tableHeaderText};
    padding: 0.75rem;
    text-align: left;
`;

const TableRow = styled.tr`
    &:nth-child(even) {
        background-color: ${(props) => props.theme.tableRowEven};
    }

    &:nth-child(odd) {
        background-color: ${(props) => props.theme.tableRowOdd};
    }
`;

const TableData = styled.td`
    padding: 0.75rem;
    border: 0.0625rem solid ${(props) => props.theme.tableBorder};
    color: ${(props) => props.theme.text};
`;

const SectionHeader = styled.h2`
    color: ${(props) => props.theme.welcomeHeader};
    margin-bottom: 1.5rem;
    font-size: 1.8rem;
    font-weight: 600;
`;

const ButtonContainer = styled.div`
    text-align: center;
    margin: ${(props) => props.theme.authButtonMargin};
`;

export default function Home() {
    return (
        <HomeContainer>
            <SectionHeader>Welcome to The Goon Squad homepage!</SectionHeader>
            <Content>
                This page is for all of my goons! Here is a rundown of each
                tab...
                <TableContainer>
                    <Table>
                        <thead>
                            <TableRow>
                                <TableHeader>Tab</TableHeader>
                                <TableHeader>Description</TableHeader>
                            </TableRow>
                        </thead>
                        <tbody>
                            <TableRow>
                                <TableData>Basic Stats</TableData>
                                <TableData>
                                    Holds basic stats on the current week of
                                    training for each athlete.
                                </TableData>
                            </TableRow>
                            <TableRow>
                                <TableData>Database</TableData>
                                <TableData>
                                    Holds all of my goon's runs since the start
                                    of data acquisition.
                                </TableData>
                            </TableRow>
                        </tbody>
                    </Table>
                </TableContainer>
            </Content>
            <ButtonContainer>
                <AuthButton />
            </ButtonContainer>
        </HomeContainer>
    );
}
