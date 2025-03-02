import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import styled from "styled-components";

import { MessageType, ROLE_TYPES } from "Constants/types/chat";

const MessageWrapper = styled.div<{ $role: ROLE_TYPES }>`
    display: flex;
    justify-content: ${(props) =>
        props.$role === "user" ? "flex-end" : "flex-start"};
    margin-bottom: 1rem;
`;

const MessageBubble = styled.div<{ $role: ROLE_TYPES }>`
    max-width: 65%;
    padding: 0.625rem;
    border-radius: 0.75rem;
    background-color: ${(props) =>
        props.$role === "user" ? "#3b82f6" : "#e5e7eb"};
    color: ${(props) => (props.$role === "user" ? "white" : "black")};
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.1);
`;

export default function Message({ content, role }: MessageType) {
    // NOTE: AI responses are markdown-formatted, so we must render them as such.
    return (
        <MessageWrapper $role={role}>
            <MessageBubble $role={role}>
                {role === ROLE_TYPES.USER ? (
                    content
                ) : (
                    <Markdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeHighlight]}
                    >
                        {content}
                    </Markdown>
                )}
            </MessageBubble>
        </MessageWrapper>
    );
}
