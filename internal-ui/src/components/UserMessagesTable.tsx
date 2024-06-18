import {MessageUser} from "../Types.ts";
import {Table, Caption, Thead, Tr, Td, Th, Tbody} from "@patternfly/react-table";
import {Link} from "react-router-dom";

interface MessagesProps {
    messages: Array<MessageUser>;
}

export const UserMessagesTable: React.FunctionComponent<MessagesProps> = ({ messages }) => { 
    return <Table
        isStriped
        isStickyHeader
    >
        <Caption>Messages</Caption>
        <Thead>
            <Tr>
                <Th width={45}>Message</Th>
                <Th width={25}>Intent</Th>
                <Th width={15}>Confidence</Th>
                <Th width={15}>Sender id</Th>
            </Tr>
        </Thead>
        <Tbody>
            {messages.map(message => (
                <Tr key={message.data.message_id}>
                    <Td>{message.data.text}</Td>
                    <Td>{message.data.parse_data.intent.name}</Td>
                    <Td>{Math.round(message.data.parse_data.intent.confidence * 100) / 100}</Td>
                    <Td><Link to={`/senders/${message.sender_id}`}>{message.sender_id.slice(0, 5)}...</Link></Td>
                </Tr>
            ))}
        </Tbody>
    </Table>;
}
