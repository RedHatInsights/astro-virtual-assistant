import {MessageUser} from "../Types.ts";
import {Table, Caption, Thead, Tr, Td, Th, Tbody} from "@patternfly/react-table";
import {Link} from "react-router-dom";

interface MessagesProps {
    messages: Array<MessageUser>;
}

export const UniqueMessages: React.FunctionComponent<MessagesProps> = ({ messages }) => {
    return <Table
        isStriped
        isStickyHeader
    >
        <Caption>User Messages</Caption>
        <Thead>
            <Tr>
                <Th>Message</Th>
                <Th>Intent</Th>
                <Th>Confidence</Th>
                <Th>Sender id</Th>
            </Tr>
        </Thead>
        <Tbody>
            {messages.map(message => (
                <Tr key={message.sender_id}>
                    <Td>{message.data.text}</Td>
                    <Td>{message.data.parse_data.intent.name}</Td>
                    <Td>{message.data.parse_data.intent.confidence}</Td>
                    <Td><Link to={`/senders/${message.sender_id}`}>{message.sender_id}</Link></Td>
                </Tr>
            ))}
        </Tbody>
    </Table>;
}
