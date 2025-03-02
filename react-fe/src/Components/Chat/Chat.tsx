import { useState } from "react";
import axios from "axios";

import { ChatContainer } from "Components/ChatContainer";
import { Conversation, MessageType, ROLE_TYPES } from "Constants/types/chat";

export default function Chat() {
    const [conversation, setConversation] = useState<Conversation | null>(null);

    /**
     * Sends a message to the bot and updates the conversation state.
     *
     * @param text The message to send to the bot.
     */
    const sendMessage = (text: string) => {
        const newMessage: MessageType = {
            role: ROLE_TYPES.USER,
            content: text,
        };
        const updatedMessages = [...(conversation?.Messages || []), newMessage];

        setConversation((prev) => {
            if (!prev) {
                return {
                    Messages: updatedMessages,
                    Options: {},
                };
            }
            return {
                ...prev,
                Messages: updatedMessages,
            };
        });

        // TODO: Test this out using debugger mode
        const body = {
            data: {
                messages: conversation?.Messages || [],
            },
            meta: {},
        };
        axios.post("http://localhost:5001/api/chat", body).then((res) => {
            console.log("AI response:", res.data.data);
            const assistantMsg: MessageType = res.data.data.response;
            const newMessages: MessageType[] = [
                ...updatedMessages,
                assistantMsg,
            ];

            setConversation((prev) => {
                if (!prev) {
                    return {
                        Messages: newMessages,
                        Options: {
                            completion_id: res.data.meta.completion_id || null,
                        },
                    };
                }
                return {
                    ...prev,
                    Messages: newMessages,
                    Options: {
                        ...prev.Options,
                        completion_id: res.data.meta.completion_id || null,
                    },
                };
            });
        });
    };

    return (
        <ChatContainer
            messages={conversation?.Messages || []}
            sendMessage={sendMessage}
        />
    );
}
