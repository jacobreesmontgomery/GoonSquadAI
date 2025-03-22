import styled from "styled-components";

import { Message } from "Components/Message";
import { MessageInput } from "Components/MessageInput";
import { MessageType } from "Constants/types/chat";

const Container = styled.div`
    display: flex;
    flex-direction: column;
    height: 90dvh; // NOTE: Probably a way to not hardcode this here (establish height in a parent element then use % here)
    background-color: ${(props) => props.theme.background};
    overflow-wrap: break-word;
    color: ${(props) => props.theme.text};
`;

const MessagesWrapper = styled.div`
    flex: 1;
    overflow-y: auto;
    padding: 16px;
`;

type ChatContainerProps = {
    messages: MessageType[];
    sendMessage: (text: string) => void;
    clearConversation: () => void;
};

export default function ChatContainer({
    messages,
    sendMessage,
    clearConversation,
}: ChatContainerProps) {
    return (
        <Container>
            <MessagesWrapper>
                {messages.map((msg, index) => (
                    <Message
                        key={index}
                        openai_message={msg.openai_message}
                        props={msg.props}
                    />
                ))}
            </MessagesWrapper>
            <MessageInput
                onSend={sendMessage}
                clearConversation={clearConversation}
            />
        </Container>
    );
}
