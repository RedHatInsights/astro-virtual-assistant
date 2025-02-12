from unittest.mock import MagicMock

import pytest

from virtual_assistant.watson import WatsonAssistantImpl, build_assistant
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

@pytest.fixture
def assistant_v2():
    return MagicMock()

@pytest.fixture
def assistant_id():
    return 'assistant_id'

@pytest.fixture
def environment_id():
    return 'environment_id'

@pytest.fixture
def watson(assistant_v2, assistant_id, environment_id) -> WatsonAssistantImpl:
    return WatsonAssistantImpl(assistant_v2, assistant_id, environment_id)

async def test_build_assistant():
    assistant = build_assistant('my_key', 'my_version', 'http://localhost')
    assert type(assistant.authenticator) is IAMAuthenticator
    assert type(assistant) is AssistantV2

async def test_create_session_with_existing_session(watson, assistant_v2):
    session_id = await watson.create_session('1234')
    assert session_id == "1234"
    assistant_v2.create_session.assert_not_called()

async def test_create_session_without_session(watson, assistant_v2):
    create_session_return = MagicMock()
    create_session_return.get_result = MagicMock(return_value={"session_id": "1234"})
    assistant_v2.create_session = MagicMock(return_value=create_session_return)

    session_id = await watson.create_session()
    assert session_id == "1234"
    assistant_v2.create_session.assert_called_once()

async def test_send_watson_message(watson, assistant_v2, assistant_id, environment_id):
    await watson.send_watson_message(session_id="1234", user_id="1234", input={})
    assistant_v2.message.assert_called_once()
    assistant_v2.message.assert_called_with(assistant_id=assistant_id, environment_id=environment_id, session_id="1234", user_id="1234", input={})
