import { useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import styled from "styled-components";
import { Database, XCircle } from "react-feather";
import ReactModal from "react-modal";

import {
    MessageProps,
    MessageType,
    OpenAIMessage,
    ROLE_TYPES,
} from "Constants/types/chat";

const MessageContainer = styled.div<{ isUser: boolean }>`
    margin-bottom: 1rem;
    display: flex;
    justify-content: ${(props) => (props.isUser ? "flex-end" : "flex-start")};
`;

const MessageBubble = styled.div<{ isUser: boolean }>`
    max-width: 80%;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    background-color: ${(props) =>
        props.isUser
            ? props.theme.messageBgUser
            : props.theme.messageBgAssistant};
    color: ${(props) =>
        props.isUser
            ? props.theme.messageTextUser
            : props.theme.messageTextAssistant};
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
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

const customStyles = {
    content: {
        top: "50%",
        left: "50%",
        right: "auto",
        bottom: "auto",
        marginRight: "-50%",
        transform: "translate(-50%, -50%)",
        maxWidth: "50%",
        fontFamily: "monospace",
        borderRadius: "0.75rem",
        boxShadow: "0 0.125rem 0.25rem rgba(0, 0, 0, 0.1)",
    },
};

export default function Message({ openai_message, props }: MessageType) {
    // NOTE: AI responses are markdown-formatted, so we must render them as such.
    const { role, content } = openai_message as OpenAIMessage;
    const { executed_query } = (props as MessageProps) || {};
    const [modalIsOpen, setIsOpen] = useState(false);

    function openModal() {
        setIsOpen(true);
    }

    function closeModal() {
        setIsOpen(false);
    }

    const isUser = openai_message.role === ROLE_TYPES.USER;

    return (
        <MessageContainer isUser={isUser}>
            <MessageBubble isUser={isUser}>
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
                    <DatabaseButton onClick={openModal}>
                        <DatabaseIcon />
                    </DatabaseButton>
                    <ReactModal
                        isOpen={modalIsOpen}
                        onRequestClose={closeModal}
                        style={customStyles}
                        contentLabel="Executed Query"
                    >
                        <XCircle
                            size={20}
                            onClick={closeModal}
                            style={{
                                cursor: "pointer",
                                position: "absolute",
                                top: "0.35rem",
                                right: "0.35rem",
                            }}
                        />
                        <h2>Here was the executed query:</h2>
                        <div>{executed_query}</div>
                    </ReactModal>
                </WidgetsContainer>
            )}
        </MessageContainer>
    );
}
