import aiohttp
import pytest
from aioresponses import aioresponses

from tests import get_resource_contents
from watson_extension.clients import AdvisorURL
from watson_extension.clients.identity import FixedUserIdentityProvider
from watson_extension.clients.insights.advisor import AdvisorClient, AdvisorClientHttp, FindRuleSort
from watson_extension.clients.platform_request import PlatformRequest


@pytest.fixture
async def aiohttp_mock():
    with aioresponses() as m:
        yield m

@pytest.fixture
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()

@pytest.fixture
async def client(session) -> AdvisorClient:
    return AdvisorClientHttp(AdvisorURL(""), FixedUserIdentityProvider(), PlatformRequest(session))

async def test_find_rule_category_by_name(client, aiohttp_mock) -> None:
    aiohttp_mock.get(
        "/api/insights/v1/rulecategory/",
        status=200,
        body=get_resource_contents('requests/insights/advisor/categories.json')
    )
    category = await client.find_rule_category_by_name("performance")
    assert category.id == 4
    assert category.name == "Performance"

async def test_find_rule_category_by_name_unknown_rule(client, aiohttp_mock) -> None:
    aiohttp_mock.get(
        "/api/insights/v1/rulecategory/",
        status=200,
        body=get_resource_contents('requests/insights/advisor/categories.json')
    )
    with pytest.raises(ValueError):
        await client.find_rule_category_by_name("unknown")

async def test_find_rules(client, aiohttp_mock) -> None:
    aiohttp_mock.get(
        "/api/insights/v1/rule?impacting=true&rule_status=enabled&limit=3",
        status=200,
        body=get_resource_contents('requests/insights/advisor/rules_0.json')
    )
    response = await client.find_rules()
    assert len(response.rules) == 3
    assert response.link == "/insights/advisor/recommendations?impacting=true&rule_status=enabled"
    assert response.rules[0].id == "ae_eol|AE_EOL_ERROR"
    assert response.rules[0].description == "Red Hat has discontinued technical support services as well as software maintenance services for the End-Of-Life Ansible Engine"
    assert response.rules[0].link == "/insights/advisor/recommendations/ae_eol|AE_EOL_ERROR"

async def test_find_rules_with_category_id(client, aiohttp_mock) -> None:
    aiohttp_mock.get(
        "/api/insights/v1/rule?impacting=true&rule_status=enabled&category=4&limit=3",
        status=200,
        body=get_resource_contents('requests/insights/advisor/rules_1.json')
    )
    response = await client.find_rules(category_id="4")
    assert len(response.rules) == 3
    assert response.link == "/insights/advisor/recommendations?impacting=true&rule_status=enabled&category=4"
    assert response.rules[0].id == "aws_nvme_io_timeout|AWS_NVME_IO_TIMEOUT_V2"
    assert response.rules[0].description == "The NVMe driver fails I/O when I/O latency exceeds operation timeout on Amazon EC2 instances"
    assert response.rules[0].link == "/insights/advisor/recommendations/aws_nvme_io_timeout|AWS_NVME_IO_TIMEOUT_V2"

async def test_find_rules_with_total_risk(client, aiohttp_mock) -> None:
    aiohttp_mock.get(
        "/api/insights/v1/rule?impacting=true&rule_status=enabled&total_risk=4&limit=3",
        status=200,
        body=get_resource_contents('requests/insights/advisor/rules_2.json')
    )
    response = await client.find_rules(total_risk=4)
    assert len(response.rules) == 3
    assert response.link == "/insights/advisor/recommendations?impacting=true&rule_status=enabled&total_risk=4"
    assert response.rules[0].id == "kernel_panic_missing_glibc|KERNEL_PANIC_MISSING_GLIBC_WARN"
    assert response.rules[0].description == "The system is unable to boot when missing glibc related components"
    assert response.rules[0].link == "/insights/advisor/recommendations/kernel_panic_missing_glibc|KERNEL_PANIC_MISSING_GLIBC_WARN"

async def test_find_rules_with_sort_and_only_workloads(client, aiohttp_mock) -> None:
    aiohttp_mock.get(
        "/api/insights/v1/rule?impacting=true&rule_status=enabled&sort=-publish_date&filter[system_profile][sap_system]=true&limit=3",
        status=200,
        body=get_resource_contents('requests/insights/advisor/rules_3.json')
    )
    response = await client.find_rules(sort=FindRuleSort.PublishDate, only_workloads=True)
    assert len(response.rules) == 3
    assert response.link == "/insights/advisor/recommendations?impacting=true&rule_status=enabled&sort=-publish_date&filter[system_profile][sap_system]=true"
    assert response.rules[0].id == "hardening_ssh_hmac_cipher_rhel8_later|SSH_INSECURE_HMAC_CIPHER_RHEL8_LATER_CRYPTO"
    assert response.rules[0].description == "SSH security is decreased when insecure cipher or hmac is enabled in the crypto policy"
    assert response.rules[0].link == "/insights/advisor/recommendations/hardening_ssh_hmac_cipher_rhel8_later|SSH_INSECURE_HMAC_CIPHER_RHEL8_LATER_CRYPTO"
