from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from fief.crypto.password import password_helper
from fief.db import AsyncSession
from fief.repositories import EmailVerificationRepository, UserRepository
from fief.services.user_manager import UserManager
from tests.data import TestData


@pytest.fixture
def user_manager(
    main_session: AsyncSession,
    send_task_mock: MagicMock,
) -> UserManager:
    return UserManager(
        password_helper=password_helper,
        user_repository=UserRepository(main_session),
        email_verification_repository=EmailVerificationRepository(main_session),
        user_fields=[],
        send_task=send_task_mock,
        audit_logger=MagicMock(),
        trigger_webhooks=MagicMock(),
        user_roles=MagicMock(),
    )


@pytest.mark.asyncio
async def test_request_verify_email_reuses_code_during_cooldown(
    test_data: TestData,
    user_manager: UserManager,
    send_task_mock: MagicMock,
    main_session: AsyncSession,
) -> None:
    user = test_data["users"]["regular_secondary"]
    repository = EmailVerificationRepository(main_session)

    assert await user_manager.request_verify_email(user, user.email) is True
    first = await repository.get_latest_by_user(user.id)
    assert first is not None

    assert await user_manager.request_verify_email(user, user.email) is False
    reused = await repository.get_latest_by_user(user.id)

    assert reused is not None
    assert reused.id == first.id
    assert reused.code == first.code
    assert len(await repository.get_by_user(user.id)) == 1
    send_task_mock.assert_called_once()


@pytest.mark.asyncio
async def test_request_verify_email_reissues_code_after_cooldown(
    test_data: TestData,
    user_manager: UserManager,
    send_task_mock: MagicMock,
    main_session: AsyncSession,
) -> None:
    user = test_data["users"]["regular_secondary"]
    repository = EmailVerificationRepository(main_session)

    assert await user_manager.request_verify_email(user, user.email) is True
    first = await repository.get_latest_by_user(user.id)
    assert first is not None

    first.created_at = datetime.now(UTC) - timedelta(minutes=10)
    await repository.update(first)

    assert await user_manager.request_verify_email(user, user.email) is True
    second = await repository.get_latest_by_user(user.id)

    assert second is not None
    assert second.id != first.id
    assert second.code != first.code
    assert len(await repository.get_by_user(user.id)) == 1
    assert send_task_mock.call_count == 2


@pytest.mark.asyncio
async def test_request_verify_email_reissues_code_for_expired_record(
    test_data: TestData,
    user_manager: UserManager,
    send_task_mock: MagicMock,
    main_session: AsyncSession,
) -> None:
    user = test_data["users"]["regular_secondary"]
    repository = EmailVerificationRepository(main_session)

    assert await user_manager.request_verify_email(user, user.email) is True
    first = await repository.get_latest_by_user(user.id)
    assert first is not None

    first.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    await repository.update(first)

    assert await user_manager.request_verify_email(user, user.email) is True
    second = await repository.get_latest_by_user(user.id)

    assert second is not None
    assert second.id != first.id
    assert len(await repository.get_by_user(user.id)) == 1
    assert send_task_mock.call_count == 2


@pytest.mark.asyncio
async def test_request_verify_email_reissues_code_when_email_changes(
    test_data: TestData,
    user_manager: UserManager,
    send_task_mock: MagicMock,
    main_session: AsyncSession,
) -> None:
    user = test_data["users"]["regular_secondary"]
    repository = EmailVerificationRepository(main_session)
    new_email = "anne+manager@nantes.city"

    assert await user_manager.request_verify_email(user, user.email) is True
    first = await repository.get_latest_by_user(user.id)
    assert first is not None

    assert await user_manager.request_verify_email(user, new_email) is True
    second = await repository.get_latest_by_user(user.id)

    assert second is not None
    assert second.id != first.id
    assert second.email == new_email
    assert len(await repository.get_by_user(user.id)) == 1

    assert await user_manager.request_verify_email(user, new_email) is False
    assert send_task_mock.call_count == 2
