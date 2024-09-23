export interface Sender {
    sender_id: string;
}

export interface Session {
    senderId: string;
    timestamp: number;
    lastTimestamp: number;
    hasSessionStarted: boolean;
    messages: Array<ValidMessage>
}

interface MessageBase<T extends string> {
    id: number;
    sender_id: string;
    type_name: T;
    timestamp: number,
    data: unknown;
}

export interface MessageAction extends MessageBase<'action'> {
    data: {
        // there is an action_text that appears to be null all the time.
        confidence: number;
        hide_rule_turn: boolean;
        metadata: MetadataBase;
        name: string;
        policy: string;
    }
}

export interface MessageActionExecutionRejected extends MessageBase<"action_execution_rejected"> {
    data: {
        confidence: number;
        metadata: MetadataBase,
        name: string;
        policy: string;
    }
}

export interface MessageActiveLoop extends MessageBase<"active_loop"> {
    data: {
        name: string;
        metadata: MetadataBase
    }
}

export interface MessageBot extends MessageBase<"bot"> {
    data: {
        data: {
            buttons: null | Array<Button>,
            custom: null | Command,
            // ... More stuff that we don't use
        },
        metadata: MetadataBase & {
            utter_action: string | null;
        },
        text: string;
    }
}

export interface MessageRestart extends MessageBase<"restart"> {
    data: {
        metadata: MetadataBase
    }
}

export interface MessageSessionStarted extends MessageBase<"session_started"> {
    data: {
        name: string;
        metadata: MetadataBase
    }
}

export interface MessageSlot extends MessageBase<"slot"> {
    data: {
        metadata: MetadataBase,
        name: string;
        value: string | boolean | number | null;
    }
}

export interface MessageUser extends MessageBase<"user"> {
    data: {
        input_channel: string;
        message_id: string;
        metadata: MetadataBase & AstroData;
        parse_data: {
            entities: Array<unknown>; // unsure about the format
            intent: Intent;
            intent_ranking: Array<Intent>;
            // ... More data
        },
        text: string;
    }
}

export interface MessageUserWithSessionData extends MessageUser {
    is_internal: boolean;
    sender_id: string;
    session_timestamp: number;
}

export interface MessageUserFeaturization extends MessageBase<"user_featurization"> {
    data: {
        metadata: MetadataBase
    }
}

export type Message = MessageAction | MessageActionExecutionRejected | MessageActiveLoop | MessageBot | MessageRestart | MessageSessionStarted | MessageSlot | MessageUser | MessageUserFeaturization;
export type ValidMessage = MessageBot | MessageUser | MessageSlot | MessageSessionStarted;

export function isTypeMessageUser(msg: Message): msg is MessageUser {
    return msg.type_name === "user" && msg.data && typeof msg.data.text === "string";
}

export function isTypeMessageBot(msg: Message): msg is MessageBot {
    return msg.type_name === "bot" && msg.data && typeof msg.data.text === "string";
}

export function isTypeMessageSlot(msg: Message): msg is MessageSlot {
    return msg.type_name === "slot" && msg.data && typeof msg.data.name === "string";
}


interface MetadataBase {
    assistant_id: string;
    model_id: string;
}

interface AstroData {
    current_url: string;
    is_org_admin: boolean;
    is_internal: boolean;
}

interface Intent {
    confidence: number;
    name: string;
}

interface Button {
    payload: string;
    title: string;
}

interface Command {
    type: "command";
    command: string;
    params: Record<string, string>;
}
