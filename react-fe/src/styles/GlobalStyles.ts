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
    navbarBackground: string;
    navbarText: string;
    navbarLinkHover: string;
    accent: string;
    tableHeader: string;
    tableHeaderText: string;
    tableRowEven: string;
    tableRowOdd: string;
    tableBorder: string;
    settingsDropdownBg: string;
    settingsDropdownBorder: string;
    buttonBackground: string;
    buttonText: string;
    buttonHover: string;
    cardBackground: string;
    headerText: string;
    shadow: string;
    homeContainer: string;
    homeContainerBorder: string;
    welcomeHeader: string;
    contentPadding: string;
    tableShadow: string;
    authButtonMargin: string;
};

export const lightTheme: Theme = {
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
    navbarBackground: "#ffffff",
    navbarText: "#fc4c02",
    navbarLinkHover: "#f0f0f0",
    accent: "#fc4c02",
    tableHeader: "#f0f0f0",
    tableHeaderText: "#333333",
    tableRowEven: "#ffffff",
    tableRowOdd: "#f8f9fa",
    tableBorder: "#e5e7eb",
    settingsDropdownBg: "#ffffff",
    settingsDropdownBorder: "#e5e7eb",
    buttonBackground: "#3b82f6",
    buttonText: "#ffffff",
    buttonHover: "#2563eb",
    cardBackground: "#ffffff",
    headerText: "#333333",
    shadow: "0 2px 10px rgba(0, 0, 0, 0.1)",
    homeContainer: "#ffffff",
    homeContainerBorder: "#e5e7eb",
    welcomeHeader: "#fc4c02",
    contentPadding: "2rem",
    tableShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
    authButtonMargin: "2rem auto",
};

export const darkTheme: Theme = {
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
    navbarBackground: "#111827",
    navbarText: "#fc4c02",
    navbarLinkHover: "#374151",
    accent: "#fc4c02",
    tableHeader: "#111827",
    tableHeaderText: "#ffffff",
    tableRowEven: "#1f2937",
    tableRowOdd: "#374151",
    tableBorder: "#4b5563",
    settingsDropdownBg: "#1f2937",
    settingsDropdownBorder: "#4b5563",
    buttonBackground: "#3b82f6",
    buttonText: "#ffffff",
    buttonHover: "#2563eb",
    cardBackground: "#374151",
    headerText: "#ffffff",
    shadow: "0 2px 10px rgba(0, 0, 0, 0.3)",
    homeContainer: "#2d3748",
    homeContainerBorder: "#4a5568",
    welcomeHeader: "#fc4c02",
    contentPadding: "2rem",
    tableShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
    authButtonMargin: "2rem auto",
};
