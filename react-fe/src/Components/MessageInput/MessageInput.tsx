import { useState } from "react";
import styled from "styled-components";

const InputContainer = styled.div`
    padding: 16px;
    background: white;
    display: flex;
    align-items: center;
    border-top: 1px solid #e5e7eb;
`;

const Input = styled.input`
    flex: 1;
    padding: 10px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    outline: none;
`;

const SendButton = styled.button`
    margin-left: 8px;
    padding: 10px 16px;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
`;

type MessageInputType = {
    onSend: (text: string) => void;
};

export default function MessageInput({ onSend }: MessageInputType) {
    const [text, setText] = useState("");

    const handleSend = () => {
        if (text.trim()) {
            onSend(text);
            setText("");
        }
    };

    return (
        <InputContainer>
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
