import { useCallback, useState } from "react";
import axios from "axios";

import { ChatContainer } from "Components/ChatContainer";
import { Conversation, MessageType, ROLE_TYPES } from "Constants/types/chat";
import ThemeProvider from "Contexts/ThemeContext";

export default function Chat() {
    const [conversation, setConversation] = useState<Conversation | null>(null);

    /**
     * Sends a message to the bot and updates the conversation state.
     *
     * @param text The message to send to the bot.
     */
    const sendMessage = (text: string) => {
        const newMessage: MessageType = {
            openai_message: {
                role: ROLE_TYPES.USER,
                content: text,
            },
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

        const body = {
            data: {
                messages:
                    updatedMessages.map(
                        (msg: MessageType) => msg.openai_message
                    ) || [],
            },
            meta: {},
        };
        axios
            .post("http://localhost:5001/api/chat/process-question", body)
            .then((res) => {
                console.log("AI response:", res.data.data);
                const assistantMsg: MessageType = {
                    openai_message: res.data.data.response,
                    props: {
                        completion_id: res.data.meta.completion_id || null,
                        executed_query: res.data.meta.executed_query || null,
                    },
                };
                const newMessages: MessageType[] = [
                    ...updatedMessages,
                    assistantMsg,
                ];

                setConversation((prev) => {
                    if (!prev) {
                        return {
                            Messages: newMessages,
                            Options: {
                                completion_id:
                                    res.data.meta.completion_id || null,
                                executed_query:
                                    res.data.meta.executed_query || null,
                            },
                        };
                    }
                    return {
                        ...prev,
                        Messages: newMessages,
                        Options: {
                            completion_id: res.data.meta.completion_id || null,
                            executed_query:
                                res.data.meta.executed_query || null,
                        },
                    };
                });
            });
    };

    const clearConversation = useCallback(() => {
        setConversation(null);
    }, [setConversation]);

    console.log("conversation:", conversation);
    return (
        <ThemeProvider>
            <ChatContainer
                messages={conversation?.Messages || []}
                sendMessage={sendMessage}
                clearConversation={clearConversation}
            />
        </ThemeProvider>
    );
}
