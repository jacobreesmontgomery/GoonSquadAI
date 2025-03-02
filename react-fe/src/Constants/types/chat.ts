export type Conversation = {
    Messages: MessageType[];
    Options: Options;
};

export enum ROLE_TYPES {
    USER = "user",
    ASSISTANT = "assistant",
    SYSTEM = "system",
    DEVELOPER = "developer",
}

// NOTE: Should match OpenAIMessage model from the chat.py model class
export type MessageType = {
    role: ROLE_TYPES;
    content: string;
};

export type Options = {
    completion_id?: number;
};
