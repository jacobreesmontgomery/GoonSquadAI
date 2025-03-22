import { useState } from "react";
import styled from "styled-components";
import { PlusCircle } from "react-feather";

const InputContainer = styled.div`
    padding: 1rem;
    background: white;
    display: flex;
    align-items: center;
    border-top: 0.0625rem solid #e5e7eb;
    gap: 0.75rem;
`;

const Input = styled.input`
    flex: 1;
    padding: 0.625rem;
    border: 0.0625rem solid #e5e7eb;
    border-radius: 0.5rem;
    outline: none;
`;

const SendButton = styled.button`
    padding: 0.625rem 1rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
`;

const NewChatButton = styled.button`
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
`;

const NewChatIcon = styled(PlusCircle)`
    height: 100%;
    padding: 0;
    margin: 0;
    background-color: none !important;
`;

type MessageInputType = {
    onSend: (text: string) => void;
    clearConversation: () => void;
};

export default function MessageInput({
    onSend,
    clearConversation,
}: MessageInputType) {
    const [text, setText] = useState("");

    const handleSend = () => {
        if (text.trim()) {
            onSend(text);
            setText("");
        }
    };

    return (
        <InputContainer>
            <NewChatButton
                title="Start a new chat."
                onClick={() => clearConversation()}
            >
                <NewChatIcon />
            </NewChatButton>
            <Input
                type="text"
                placeholder="Type a message..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
            />
            <SendButton onClick={handleSend}>Send</SendButton>
        </InputContainer>
    );
}
