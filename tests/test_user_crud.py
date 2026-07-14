from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest

from cruds.user import fetch_user_by_email
from models.user import User


@pytest.mark.anyio
async def test_fetch_user_by_email():
    mock_db = AsyncMock()
    expected_user = User(
        user_id=uuid.uuid4(), user_name="rintaro", email="test@test.com"
    )

    mock_result = MagicMock()
    mock_db.execute.return_value = mock_result

    mock_scalars = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_scalars.first.return_value = expected_user

    retrieved_user = await fetch_user_by_email("test@test.com", mock_db)

    assert retrieved_user.user_name == "rintaro"
    assert retrieved_user.email == "test@test.com"

    mock_db.execute.assert_called_once()
