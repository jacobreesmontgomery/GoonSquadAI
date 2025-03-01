import { useState } from "react";
import axios from "axios";

import { ChatContainer } from "Components/ChatContainer";
import { Conversation, MessageType, USER_TYPES } from "Constants/types/chat";

export default function Chat() {
    const [conversation, setConversation] = useState<Conversation | null>(null);

    /**
     * Sends a message to the bot and updates the conversation state.
     *
     * @param text The message to send to the bot.
     */
    const sendMessage = (text: string) => {
        const newMessage: MessageType = { text, sender: USER_TYPES.USER };
        const updatedMessages = [...(conversation?.Messages || []), newMessage];

        setConversation((prev) => {
            if (!prev) {
                return {
                    Messages: updatedMessages,
                    Options: { completion_id: 0 },
                };
            }
            return {
                ...prev,
                Messages: updatedMessages,
            };
        });

        // TODO: I think I should update this conversation messages structure to match that of
        // OpenAI's chat completion structure. Example 'messages' attribute:
        /*
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi there! How can I help?"},
                {"role": "user", "content": "Tell me about AI."}
            ]
        */
        const body = {
            data: {
                text: text,
            },
            meta: {
                completion_id:
                    conversation?.Options?.completion_id || undefined,
            },
        };
        axios.post("http://localhost:5001/api/chat", body).then((res) => {
            console.log("AI response:", res.data.data);
            const botMessage: MessageType = {
                text: res.data.data.response,
                sender: USER_TYPES.BOT,
            };
            const newMessages = [...updatedMessages, botMessage];

            setConversation((prev) => {
                if (!prev) {
                    return {
                        Messages: newMessages,
                        Options: { completion_id: res.data.meta.completion_id },
                    };
                }
                return {
                    ...prev,
                    Messages: newMessages,
                    Options: {
                        ...prev.Options,
                        completion_id: res.data.meta.completion_id,
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
