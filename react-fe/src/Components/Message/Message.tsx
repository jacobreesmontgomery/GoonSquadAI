import { useCallback, useMemo, useState } from "react";
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
    flex-direction: ${(props) => (props.isUser ? "row" : "column")};
`;

const MessageBubble = styled.div<{ isUser: boolean }>`
    position: relative;
    max-width: 60%;
    width: fit-content;
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
    box-shadow: 0 0.0625rem 0.125rem rgba(0, 0, 0, 0.1);
`;

const DatabaseButton = styled.button`
    padding: 0;
    border: none;
    background-color: transparent;
    color: inherit;
    cursor: pointer;
    display: flex;
    opacity: 0.7;

    &:hover {
        opacity: 1;
    }
`;

const ButtonsContainer = styled.div`
    position: absolute;
    top: 0.35rem;
    right: 0.35rem;
    display: flex;
    gap: 0.5rem;
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
    const { executed_query, query_results, query_confidence } =
        (props as MessageProps) || {};
    const [modalIsOpen, setIsOpen] = useState(false);
    const [modalType, setModalType] = useState<"database" | null>(null);

    const openModal = useCallback(() => {
        setModalType("database");
        setIsOpen(true);
    }, []);

    const closeModal = useCallback(() => {
        setModalType(null);
        setIsOpen(false);
    }, []);

    const isUser = useMemo(
        () => openai_message.role === ROLE_TYPES.USER,
        [openai_message.role]
    );

    return (
        <MessageContainer isUser={isUser}>
            <MessageBubble isUser={isUser}>
                {role === ROLE_TYPES.USER ? (
                    content
                ) : (
                    <>
                        {(executed_query || query_results) && (
                            <ButtonsContainer>
                                {(executed_query || query_results) && (
                                    <DatabaseButton onClick={openModal}>
                                        <DatabaseIcon size={16} />
                                    </DatabaseButton>
                                )}
                            </ButtonsContainer>
                        )}
                        <Markdown
                            remarkPlugins={[remarkGfm]}
                            rehypePlugins={[rehypeHighlight]}
                        >
                            {content}
                        </Markdown>
                    </>
                )}

                <ReactModal
                    isOpen={modalIsOpen}
                    onRequestClose={closeModal}
                    style={customStyles}
                    contentLabel="Database Information"
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
                    {query_confidence && (
                        <h2>Query Confidence: {query_confidence}</h2>
                    )}
                    {executed_query && (
                        <>
                            <h2>Executed Query:</h2>
                            <div>{executed_query}</div>
                        </>
                    )}
                    {query_results && (
                        <>
                            <h2>Query Results:</h2>
                            <pre>{JSON.stringify(query_results, null, 2)}</pre>
                        </>
                    )}
                </ReactModal>
            </MessageBubble>
        </MessageContainer>
    );
}
