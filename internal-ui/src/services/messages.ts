import axios from 'axios';
import {Session, ValidMessage} from "../Types.ts";
import {useReducer, useEffect, Dispatch} from 'react';

const FilterTypeName: Array<ValidMessage["type_name"]> = [
    "bot",
    "user",
    "slot",
    "session_started"
];


const REQUEST_LIMIT = 1000;

const getMessages = async (senderId?: string, cursor?: number): Promise<Array<ValidMessage>> => {
    const request = senderId ? `/api/virtual-assistant/v1/messages/${senderId}` : `/api/virtual-assistant/v1/messages`;

    const response = await axios.get(request,{
        params: {
            cursor: cursor,
            type_name: FilterTypeName.join(','),
            limit: REQUEST_LIMIT
        }
    });
    if (response.status === 200) {
        return response.data.messages;
    }

    throw new Error('Invalid request');
};

export const getSessionsInRange = async (senderId?: string, start?: number, end?: number): Promise<Array<Session>> => {
    const messages = await getMessagesInRange(senderId, start, end);
    return addMessages([], messages);
}

export const getMessagesInRange = async (senderId?: string, start?: number, end?: number): Promise<Array<ValidMessage>> => {
    const request = senderId ? `/api/virtual-assistant/v1/messages/${senderId}` : `/api/virtual-assistant/v1/messages`;
    const sendRequest = async (start?: number, end?: number, offset?: number, limit?: number): Promise<RequestedMessageResponse> => {
        const response = await axios.get(request,{
            params: {
                start_date: start,
                end_date: end,
                type_name: FilterTypeName.join(','),
                offset: offset,
                limit: limit
            }
        });
        
        return {
            messages: response.data.messages,
            count: response.data.count,
            status: response.status
        };
    };

    const messages = [];
    let count = 0;
    let offset = 0;

    do {
        const response = await sendRequest(start, end, offset, REQUEST_LIMIT);
        if (response.status != 200) {
            throw new Error('Invalid request');
        }
        count = response.count;
        messages.push(...response.messages);
        offset += REQUEST_LIMIT;
        await new Promise(resolve => setTimeout(resolve, 100)); // sleep for 100ms
    }
    while (offset < count);

    return messages;
}

interface RequestedMessageResponse {
    messages: Array<ValidMessage>;
    count: number;
    status: number;
}

interface MessageResponse {
    isFirstLoad: boolean;
    isLoading: boolean;
    sessions: ReadonlyArray<Session>;
    loadMore: () => void;
}

interface ReducerState {
    isFirstLoad: boolean;
    isLoading: boolean;
    sessions: ReadonlyArray<Session>;
}

type ActionType = {
    kind: 'start_load'
} | {
    kind: 'start_load_after';
} | {
    kind: 'load_finished';
    messages: ReadonlyArray<ValidMessage>;
};

const initialLoad = async (senderId: string | undefined, dispatch: Dispatch<ActionType>) => {
    const messages = await getMessages(senderId);
    dispatch({
        kind: 'load_finished',
        messages: messages
    });
}

const loadMore = async (senderId: string | undefined, cursor: number, dispatch: Dispatch<ActionType>) => {
    const messages = await getMessages(senderId, cursor);
    dispatch({
        kind: 'load_finished',
        messages: messages
    });
}

const addMessages = (sessions: ReadonlyArray<Session>, messages: ReadonlyArray<ValidMessage>) => {
    const allMessages = sessions
        .flatMap(s => s.messages)
        .concat(...messages)
        .sort((m1, m2) => m1.id - m2.id)
        .filter((m, i, arr) => !i || m.id != arr[i - 1].id);

    const newSessions: Array<Session> = [];
    allMessages.forEach(m => {
        const firstSessionFromSender = newSessions.findIndex(s => s.senderId === m.sender_id);

        if (firstSessionFromSender === -1 || m.type_name === "session_started") {
            newSessions.unshift({
                senderId: m.sender_id,
                messages: [m],
                timestamp: m.timestamp,
                hasSessionStarted: m.type_name === "session_started"
            });
        } else {
            newSessions[firstSessionFromSender].messages.push(m);
        }
    });

    return newSessions;
}

const reducer = (state: ReducerState, action: ActionType): ReducerState => {
    if (state.isFirstLoad && action.kind !== "load_finished") {
        return state;
    }

    if (action.kind === "start_load") {
        return {
            ...state,
            isFirstLoad: true,
            sessions: [],
        }
    } else if (action.kind === "load_finished") {
        return {
            ...state,
            isFirstLoad: false,
            isLoading: false,
            sessions: addMessages(state.sessions, action.messages)
        };
    } else if (action.kind === "start_load_after") {
        return {
            ...state,
            isLoading: true,
        }
    }

    return state;
}

const initialState: ReducerState = {
    isFirstLoad: false,
    isLoading: false,
    sessions: []
}

export const useMessages = (senderId?: string): MessageResponse => {
    const [state, dispatch] = useReducer(reducer, initialState);

    useEffect(() => {
        dispatch({
            kind: "start_load"
        });
    }, []);

    useEffect(() => {
        if (state.isFirstLoad) {
            void initialLoad(senderId, dispatch);
        }
    }, [state.isFirstLoad, senderId]);

    useEffect(() => {
        if (state.isLoading) {
            if (state.sessions.length > 0 && state.sessions[state.sessions.length - 1].messages.length > 0) {
                const lastSessionIndex = state.sessions.length - 1;
                void loadMore(senderId, state.sessions[lastSessionIndex].messages[0].id, dispatch);
            }
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [state.isLoading, senderId]);

    return {
        ...state,
        loadMore: () => dispatch({
            kind: "start_load_after",
        })
    }
};
