import styled from "styled-components";
import { Moon, Sun } from "react-feather";
import { useTheme } from "Contexts/ThemeContext";

const ToggleButton = styled.button`
    background: none;
    border: none;
    cursor: pointer;
    color: ${(props) => props.theme.text};
    padding: 0;
`;

export default function ThemeToggle() {
    const { theme, toggleTheme } = useTheme();

    return (
        <ToggleButton onClick={toggleTheme} title="Toggle dark mode">
            {theme === "light" ? <Moon size={20} /> : <Sun size={20} />}
        </ToggleButton>
    );
}
