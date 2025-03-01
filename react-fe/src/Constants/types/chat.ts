export type Conversation = {
    Messages: MessageType[];
    Options: Options;
};

export enum USER_TYPES {
    USER = "user",
    BOT = "bot",
}

export type MessageType = {
    text: string;
    sender: USER_TYPES;
};

export type Options = {
    completion_id: number;
};
