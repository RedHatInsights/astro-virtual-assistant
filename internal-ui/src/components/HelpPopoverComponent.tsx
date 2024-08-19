import React from 'react';
import { Popover } from '@patternfly/react-core';
import { OutlinedQuestionCircleIcon } from '@patternfly/react-icons';

interface HelpPopoverProps {
    content: string;
    title: string;
}

export const HelpPopover: React.FunctionComponent<HelpPopoverProps> = ({ content, title }) => (
    <Popover
        aria-label="Popover question"
        headerContent={title}
        bodyContent={content}
    >
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <a>
                <OutlinedQuestionCircleIcon />
            </a>
        </div>
    </Popover>
)