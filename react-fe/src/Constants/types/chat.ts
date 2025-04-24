export type Conversation = {
    Messages: MessageType[];
    Options: MessageProps;
};

export enum ROLE_TYPES {
    USER = "user",
    ASSISTANT = "assistant",
    SYSTEM = "system",
    DEVELOPER = "developer",
}

export type OpenAIMessage = {
    role: ROLE_TYPES;
    content: string;
};

export type MessageProps = {
    completion_id?: number;
    executed_query?: string;
    query_results?: string;
    query_confidence?: string;
    answer_confidence?: string;
};

// NOTE: Should match OpenAIMessage model from the chat.py model class
export type MessageType = {
    openai_message: OpenAIMessage;
    props?: MessageProps;
};
