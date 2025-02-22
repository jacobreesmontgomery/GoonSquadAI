import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthResult } from "Components/AuthResult";
import { Home } from "Components/Home";
import { BasicStats } from "Components/BasicStats";
import { Database } from "Components/Database";
import { Navbar } from "Components/Navbar";
import "./App.css";

export default function App() {
    return (
        <Router>
            <Navbar />
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/basic-stats" element={<BasicStats />} />
                <Route path="/detailed-stats" element={<Database />} />
                <Route path="/new-athlete-result" element={<AuthResult />} />
            </Routes>
        </Router>
    );
}
