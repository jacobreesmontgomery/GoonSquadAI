import { useState } from "react";
import styled from "styled-components";
import { PlusCircle } from "react-feather";
import { ThemeToggle } from "Components/ThemeToggle";

const InputContainer = styled.div`
    padding: 1rem;
    background: ${(props) => props.theme.inputBackground};
    display: flex;
    align-items: center;
    border-top: 0.0625rem solid ${(props) => props.theme.containerBorder};
    gap: 0.75rem;
`;

const Input = styled.input`
    flex: 1;
    padding: 0.625rem;
    border: 0.0625rem solid ${(props) => props.theme.inputBorder};
    border-radius: 0.5rem;
    outline: none;
    background-color: ${(props) => props.theme.inputBackground};
    color: ${(props) => props.theme.text};

    &::placeholder {
        color: ${(props) => props.theme.text}80;
    }
`;

const SendButton = styled.button`
    padding: 0.625rem 1rem;
    background-color: ${(props) => props.theme.primary};
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
    color: ${(props) => props.theme.text};
`;

const NewChatIcon = styled(PlusCircle)`
    height: 100%;
    padding: 0;
    margin: 0;
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
            <ThemeToggle />
        </InputContainer>
    );
}
