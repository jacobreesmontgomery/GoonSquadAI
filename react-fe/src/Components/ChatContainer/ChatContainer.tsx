import styled from "styled-components";
import { Message } from "Components/Message";
import { MessageInput } from "Components/MessageInput";

type MessageType = {
    text: string;
    sender: "user" | "bot";
};

const Container = styled.div`
    display: flex;
    flex-direction: column;
    height: 90dvh; // NOTE: Probably a way to not hardcode this here (establish height in a parent element then use % here)
    background-color: #f3f4f6;
    overflow-wrap: break-word;
`;

const MessagesWrapper = styled.div`
    flex: 1;
    overflow-y: auto;
    padding: 16px;
`;

type ChatContainerProps = {
    messages: MessageType[];
    sendMessage: (text: string) => void;
};

export default function ChatContainer({
    messages,
    sendMessage,
}: ChatContainerProps) {
    return (
        <Container>
            <MessagesWrapper>
                {messages.map((msg, index) => (
                    <Message key={index} text={msg.text} sender={msg.sender} />
                ))}
            </MessagesWrapper>
            <MessageInput onSend={sendMessage} />
        </Container>
    );
}
