import axios from 'axios';
import {Sender} from "../Types.ts";
import {useQuery} from '@tanstack/react-query';


const getSenders = async (): Promise<Array<Sender>> => {
    const response = await axios.get(`/api/virtual-assistant/v1/senders`);
    if (response.status === 200) {
        return response.data.senders;
    }

    throw new Error('Invalid request');
};

export const useSenders = () => {
    return useQuery({
        queryKey: ['senders'],
        queryFn: getSenders
    });
};
