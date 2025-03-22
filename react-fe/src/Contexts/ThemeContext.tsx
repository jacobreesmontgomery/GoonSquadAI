import {
    createContext,
    useState,
    useContext,
    ReactNode,
    useCallback,
    useEffect,
    useMemo,
} from "react";
import { ThemeProvider as StyledThemeProvider } from "styled-components";
import { lightTheme, darkTheme, ThemeMode } from "../styles/GlobalStyles";

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
    const [theme, setTheme] = useState<ThemeMode>(() => {
        const savedTheme = localStorage.getItem("theme") as ThemeMode;
        return savedTheme === "light" || savedTheme === "dark"
            ? savedTheme
            : "dark";
    });

    useEffect(() => {
        localStorage.setItem("theme", theme);
    }, [theme]);

    const toggleTheme = useCallback(() => {
        setTheme((prevTheme) => (prevTheme === "light" ? "dark" : "light"));
    }, []);

    const themeObject = useMemo(
        () => (theme === "light" ? lightTheme : darkTheme),
        [theme]
    );

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
            <StyledThemeProvider theme={themeObject}>
                {children}
            </StyledThemeProvider>
        </ThemeContext.Provider>
    );
}
