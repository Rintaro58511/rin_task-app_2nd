from unittest.mock import AsyncMock

import pytest

from enums import TaskStatus
from service.subtasks import check_progress


@pytest.mark.anyio
async def test_check_progress():
    mock_db_half = AsyncMock()
    test_progress_ratio_half = await check_progress(50, mock_db_half)
    assert test_progress_ratio_half == TaskStatus.IN_PROGRESS

    mock_db_all = AsyncMock()
    test_progress_ratio_all = await check_progress(100, mock_db_all)
    assert test_progress_ratio_all == TaskStatus.DONE

    mock_db_zero = AsyncMock()
    test_progress_ratio_zero = await check_progress(0, mock_db_zero)
    assert test_progress_ratio_zero == TaskStatus.TODO
