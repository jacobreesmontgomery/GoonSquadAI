import styled from "styled-components";
import { Settings } from "react-feather";
import { useState, useRef, useEffect } from "react";
import ThemeToggle from "Components/ThemeToggle/ThemeToggle";
import { useTheme } from "Contexts/ThemeContext";

const NavbarContainer = styled.div`
    background-color: #333;
    padding: 0.625rem;
    color: #fc4c02;
    display: flex;
    justify-content: space-between;
    align-items: center;
`;

const NavbarTitle = styled.h1`
    margin: 0;
    height: 100%;
`;

const NavbarLinks = styled.div`
    display: flex;
    gap: 1.25rem;
`;

const NavbarLink = styled.a`
    color: #fc4c02;
    text-decoration: none;
    padding: 0.3125rem 0.625rem;
    border-radius: 0.3125rem;

    &:hover {
        background-color: #575757;
    }
`;

const SettingsButton = styled.button`
    background: none;
    border: none;
    cursor: pointer;
    color: #fc4c02;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.3125rem;
    border-radius: 0.3125rem;

    &:hover {
        background-color: #575757;
    }
`;

const SettingsDropdown = styled.div`
    position: absolute;
    right: 0.625rem;
    top: 3.125rem;
    background-color: ${(props) => props.theme.background || "#444"};
    border: 0.0625rem solid ${(props) => props.theme.border || "#666"};
    border-radius: 0.3125rem;
    padding: 0.625rem;
    z-index: 1000;
    box-shadow: 0 0.125rem 0.625rem rgba(0, 0, 0, 0.2);
    min-width: 10rem;
`;

const SettingsItem = styled.div`
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0.3125rem;
    color: ${(props) => props.theme.text || "#fc4c02"};
    border-bottom: 0.0625rem solid ${(props) => props.theme.border || "#555"};
    gap: 1rem;

    &:last-child {
        border-bottom: none;
    }
`;

export default function Navbar() {
    const [settingsOpen, setSettingsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const { theme } = useTheme();

    const toggleSettings = () => {
        setSettingsOpen(!settingsOpen);
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(event.target as Node)
            ) {
                setSettingsOpen(false);
            }
        }

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [dropdownRef]);

    return (
        <NavbarContainer>
            <NavbarTitle>Strava API</NavbarTitle>
            <NavbarLinks>
                <NavbarLink href="/">Home</NavbarLink>
                <NavbarLink href="/chat">Chat</NavbarLink>
                <NavbarLink href="/basic-stats">Basic Stats</NavbarLink>
                <NavbarLink href="/detailed-stats">Database</NavbarLink>
                <SettingsButton onClick={toggleSettings} title="Settings">
                    <Settings size={20} />
                </SettingsButton>
                {settingsOpen && (
                    <SettingsDropdown ref={dropdownRef}>
                        <SettingsItem>
                            <span>
                                {theme === "light"
                                    ? "Toggle Dark Mode"
                                    : "Toggle Light Mode"}
                            </span>
                            <ThemeToggle />
                        </SettingsItem>
                    </SettingsDropdown>
                )}
            </NavbarLinks>
        </NavbarContainer>
    );
}
