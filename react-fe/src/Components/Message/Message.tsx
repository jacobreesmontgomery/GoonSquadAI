import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import styled from "styled-components";

import { USER_TYPES } from "Constants/types/chat";

const MessageWrapper = styled.div<{ $sender: USER_TYPES }>`
    display: flex;
    justify-content: ${(props) =>
        props.$sender === "user" ? "flex-end" : "flex-start"};
    margin-bottom: 1rem;
`;

const MessageBubble = styled.div<{ $sender: USER_TYPES }>`
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
    sender: USER_TYPES;
};

export default function Message({ text, sender }: MessageProps) {
    // NOTE: AI responses are markdown-formatted, so we must render them as such.
    return (
        <MessageWrapper $sender={sender}>
            <MessageBubble $sender={sender}>
                {sender === USER_TYPES.USER ? (
                    text
                ) : (
                    <Markdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeHighlight]}
                    >
                        {text}
                    </Markdown>
                )}
            </MessageBubble>
        </MessageWrapper>
    );
}
