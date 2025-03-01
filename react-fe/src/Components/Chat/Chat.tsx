import { useState } from "react";
import axios from "axios";

import { ChatContainer } from "Components/ChatContainer";

type MessageType = {
    text: string;
    sender: "user" | "bot";
};

export default function Chat() {
    const [messages, setMessages] = useState<MessageType[]>([]);

    /**
     * Sends a message to the bot and updates the messages state.
     *
     * @param text The message to send to the bot.
     */
    const sendMessage = (text: string) => {
        const newMessage: MessageType = { text, sender: "user" };
        setMessages((prev) => [...prev, newMessage]);

        axios.post("http://localhost:5001/api/chat", { text }).then((res) => {
            console.log("AI response:", res.data.data);
            setMessages((prev) => [
                ...prev,
                { text: res.data.data.response, sender: "bot" },
            ]);
        });
    };

    return <ChatContainer messages={messages} sendMessage={sendMessage} />;
}
