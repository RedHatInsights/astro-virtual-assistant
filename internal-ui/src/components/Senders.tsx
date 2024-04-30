import {Sender} from "../Types.ts";
import {Table, Caption, Thead, Tr, Td, Th, Tbody} from "@patternfly/react-table";
import {Link} from "react-router-dom";

interface SendersProps {
    senders: ReadonlyArray<Sender>;
}

export const Senders: React.FunctionComponent<SendersProps> = ({senders}) => {
    return <Table
        isStriped
        isStickyHeader
    >
        <Caption>Senders list</Caption>
        <Thead>
            <Tr>
                <Th>Sender id</Th>
            </Tr>
        </Thead>
        <Tbody>
            {senders.map(sender => (
                <Tr key={sender.sender_id}>
                    <Td><Link to={`/senders/${sender.sender_id}`}>{sender.sender_id}</Link></Td>
                </Tr>
            ))}
        </Tbody>
    </Table>;
}
