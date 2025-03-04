import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import styled from "styled-components";
import { Database } from "react-feather";

import {
    MessageProps,
    MessageType,
    OpenAIMessage,
    ROLE_TYPES,
} from "Constants/types/chat";

const MessageWrapper = styled.div<{ $role: ROLE_TYPES }>`
    display: flex;
    justify-content: ${(props) =>
        props.$role === ROLE_TYPES.USER ? "flex-end" : "flex-start"};
    margin-bottom: 1rem;
    flex-direction: ${(props) =>
        props.$role === ROLE_TYPES.ASSISTANT && "column"};
`;

const MessageBubble = styled.div<{ $role: ROLE_TYPES }>`
    max-width: 65%;
    width: fit-content;
    padding: 0.625rem;
    border-radius: 0.75rem;
    background-color: ${(props) =>
        props.$role === "user" ? "#3b82f6" : "#e5e7eb"};
    color: ${(props) => (props.$role === "user" ? "white" : "black")};
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.1);
`;

const WidgetsContainer = styled.div`
    width: fit-content;
    display: flex;
    align-items: start;
    padding: 0.1rem;
    margin-top: 0.25rem;
    border-radius: 0.75rem;
    background-color: #f3f4f6;
    color: black;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.1);
`;

const DatabaseButton = styled.button`
    padding: 0;
    border: none;
    background-color: #f3f4f6;
    color: black;
    cursor: pointer;
`;

const DatabaseIcon = styled(Database)`
    padding: 0;
`;

export default function Message({ openai_message, props }: MessageType) {
    // NOTE: AI responses are markdown-formatted, so we must render them as such.
    const { role, content } = openai_message as OpenAIMessage;
    const { executed_query } = (props as MessageProps) || {};
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
            {executed_query && (
                <WidgetsContainer>
                    <DatabaseButton onClick={() => console.log(executed_query)}>
                        <DatabaseIcon />
                    </DatabaseButton>
                </WidgetsContainer>
            )}
        </MessageWrapper>
    );
}
