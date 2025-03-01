import { useState } from "react";
import { ChatContainer } from "Components/ChatContainer";

type MessageType = {
    text: string;
    sender: "user" | "bot";
};

export default function Chat() {
    const [messages, setMessages] = useState<MessageType[]>([]);

    const sendMessage = (text: string) => {
        const newMessage: MessageType = { text, sender: "user" };
        setMessages((prev) => [...prev, newMessage]);

        // TODO - JACOB: Update this to call on the BE for processing
        // Simulated bot response
        setTimeout(() => {
            setMessages((prev) => [
                ...prev,
                { text: "This is a bot response.", sender: "bot" },
            ]);
        }, 1000);
    };

    return <ChatContainer messages={messages} sendMessage={sendMessage} />;
}
