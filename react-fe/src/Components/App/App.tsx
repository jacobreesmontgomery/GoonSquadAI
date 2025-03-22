import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Chat } from "Components/Chat";
import { Home } from "Components/Home";
import { BasicStats } from "Components/BasicStats";
import { Database } from "Components/Database";
import { AuthResult } from "Components/AuthResult";
import { Navbar } from "Components/Navbar";
import ThemeProvider from "Contexts/ThemeContext";
import styled, { createGlobalStyle } from "styled-components";

const GlobalStyle = createGlobalStyle`
  body {
    margin: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f4f4f9;
    color: #333333;
  }
`;

const AppContainer = styled.div`
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
`;

export default function App() {
    return (
        <AppContainer>
            <GlobalStyle />
            <ThemeProvider>
                <Router>
                    <Navbar />
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/chat" element={<Chat />} />
                        <Route path="/basic-stats" element={<BasicStats />} />
                        <Route path="/detailed-stats" element={<Database />} />
                        <Route
                            path="/new-athlete-result"
                            element={<AuthResult />}
                        />
                    </Routes>
                </Router>
            </ThemeProvider>
        </AppContainer>
    );
}
