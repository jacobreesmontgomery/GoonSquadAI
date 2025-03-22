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
};
