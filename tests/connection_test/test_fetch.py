import pytest
from httpx import ASGITransport, AsyncClient

from main import app

@pytest.mark.anyio
async def test_search_other_user_subtask(
    connection_test,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask = connection_test

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get(
                f"/tasks/subtasks/{test_subtask.subtask_id}"
            )
    assert response.status_code == 404
