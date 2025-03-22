import {
    createContext,
    useState,
    useContext,
    ReactNode,
    useCallback,
} from "react";
import { ThemeProvider as StyledThemeProvider } from "styled-components";

export type ThemeMode = "light" | "dark";
export type Theme = {
    background: string;
    inputBackground: string;
    text: string;
    inputBorder: string;
    primary: string;
    messageBgUser: string;
    messageBgAssistant: string;
    messageTextUser: string;
    messageTextAssistant: string;
    containerBorder: string;
};

// Define theme colors
const lightTheme: Theme = {
    background: "#f3f4f6",
    inputBackground: "#ffffff",
    text: "#000000",
    inputBorder: "#e5e7eb",
    primary: "#3b82f6",
    messageBgUser: "#3b82f6",
    messageBgAssistant: "#ffffff",
    messageTextUser: "#ffffff",
    messageTextAssistant: "#000000",
    containerBorder: "#e5e7eb",
};

const darkTheme: Theme = {
    background: "#1f2937",
    inputBackground: "#374151",
    text: "#ffffff",
    inputBorder: "#4b5563",
    primary: "#3b82f6",
    messageBgUser: "#3b82f6",
    messageBgAssistant: "#374151",
    messageTextUser: "#ffffff",
    messageTextAssistant: "#ffffff",
    containerBorder: "#4b5563",
};

type ThemeContextType = {
    theme: ThemeMode;
    toggleTheme: () => void;
};

const ThemeContext = createContext<ThemeContextType>({
    theme: "light",
    toggleTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

type ThemeProviderProps = {
    children: ReactNode;
};

export default function ThemeProvider({ children }: ThemeProviderProps) {
    const [theme, setTheme] = useState<ThemeMode>("dark");

    const toggleTheme = useCallback(() => {
        setTheme((prevTheme) => (prevTheme === "light" ? "dark" : "light"));
    }, []);

    const themeObject = theme === "light" ? lightTheme : darkTheme;

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
            <StyledThemeProvider theme={themeObject}>
                {children}
            </StyledThemeProvider>
        </ThemeContext.Provider>
    );
}
