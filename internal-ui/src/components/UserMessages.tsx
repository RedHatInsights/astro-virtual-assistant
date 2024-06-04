import { SearchInput, Checkbox } from "@patternfly/react-core";
import {MessageUser} from "../Types.ts";
import {Table, Caption, Thead, Tr, Td, Th, Tbody} from "@patternfly/react-table";
import {Link} from "react-router-dom";

interface MessagesProps {
    messages: Array<MessageUser>;
    isExternal: boolean;
    searchValue: string;
    updateFilters: (isExternal: boolean, searchValue: string) => void;
}

export const UserMessages: React.FunctionComponent<MessagesProps> = ({ messages, isExternal, searchValue, updateFilters }) => {
    const onChange = (value: string) => {
        updateFilters(isExternal, value);
    };
    
    return <Table
        isStriped
        isStickyHeader
    >
        <Caption>Messages</Caption>
        <Thead>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 20 }}>
                <SearchInput
                    placeholder="Search by Keyword"
                    value={searchValue}
                    onChange={(_event, value) => onChange(value)}
                    onClear={() => onChange('')}
                />
                <Checkbox
                    id="toggle-external-only"
                    label="External Only"
                    isChecked={isExternal}
                    onChange={(_event, checked) => updateFilters(checked, searchValue)}
                />
            </div>
            <Tr>
                <Th>Message</Th>
                <Th>Intent</Th>
                <Th>Confidence</Th>
                <Th>Sender id</Th>
            </Tr>
        </Thead>
        <Tbody>
            {messages.map(message => (
                <Tr key={message.data.message_id}>
                    <Td>{message.data.text}</Td>
                    <Td>{message.data.parse_data.intent.name}</Td>
                    <Td>{message.data.parse_data.intent.confidence}</Td>
                    <Td><Link to={`/senders/${message.sender_id}`}>{message.sender_id}</Link></Td>
                </Tr>
            ))}
        </Tbody>
    </Table>;
}
