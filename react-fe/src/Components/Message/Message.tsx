import styled from "styled-components";

const MessageWrapper = styled.div<{ $sender: "user" | "bot" }>`
    display: flex;
    justify-content: ${(props) =>
        props.$sender === "user" ? "flex-end" : "flex-start"};
    margin-bottom: 1rem;
`;

const MessageBubble = styled.div<{ $sender: "user" | "bot" }>`
    max-width: 65%;
    padding: 0.625rem;
    border-radius: 0.75rem;
    background-color: ${(props) =>
        props.$sender === "user" ? "#3b82f6" : "#e5e7eb"};
    color: ${(props) => (props.$sender === "user" ? "white" : "black")};
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.1);
`;

type MessageProps = {
    text: string;
    sender: "user" | "bot";
};

export default function Message({ text, sender }: MessageProps) {
    return (
        <MessageWrapper $sender={sender}>
            <MessageBubble $sender={sender}>{text}</MessageBubble>
        </MessageWrapper>
    );
}
