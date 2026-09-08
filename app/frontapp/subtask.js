const taskList = document.getElementById("taskList");
const createSubTaskForm = document.getElementById("createSubTaskForm");

async function addSubTask(taskId, subTaskName){
    
    const token = getToken();

    const subTaskData = {
        subtask_name: subTaskName,
        is_complete: false,
    };

    try {
        const response = await send_request({
            method: "POST",
            token: token,
            url: `${apiUrl}/${taskId}/subtask`,
            body: subTaskData,
        });

        if (response.ok) {
            await fetchAndDisplaySubTasks(taskId);
            await refreshTask(taskId);

            return true;
        }else if(response.status === 401) {
            alert("認証エラーが発生しました。再度ログインしてください。");
            localStorage.removeItem('token');
            window.location.href = "./login.html";

            return false;
        } else {
            const err = await response.json();
            alert(err.detail || "サブタスクの追加に失敗しました");

            return false;
        }
    } catch (error) {
        console.error("サブタスク追加中にエラーが発生しました", error);

        return false;
    }
}

document.getElementById("taskList").addEventListener("change", async function(event){

    if(!event.target.classList.contains("subTaskCheck")) {
        return;
    }

    const subTaskId = event.target.dataset.id;
    const taskId = event.target.dataset.taskId;
    const isComplete = event.target.checked;
    const subTaskName = event.target.dataset.name;

    await updateSubTask(
        taskId, subTaskId, subTaskName, isComplete
    );

});

async function updateSubTask(taskId, subTaskId, subTaskName, isComplete){

    const token = getToken();

    const subTaskData = {
        subtask_name: subTaskName,
        is_complete: isComplete,
    };

    try {
        const response = await send_request({
            method: 'PUT',
            token: token,
            url: `${apiUrl}/${taskId}/subtasks/${subTaskId}`,
            body: subTaskData
        });

        if (response.ok) {
            await fetchAndDisplaySubTasks(taskId);
            await refreshTask(taskId);
        }else if(response.status === 401) {
            alert("認証エラーが発生しました。再度ログインしてください。");
            localStorage.removeItem('token');
            window.location.href = "./login.html";
        } else {
            const err = await response.json();
            alert(err.detail || "サブタスクの更新に失敗しました");
        }
    } catch (error) {
        console.error('タスク更新中にエラーが発生しました', error);
    }
}

document.getElementById("taskList").addEventListener("click", async function(event){

    console.log(
        "CLICK:",
        event.target.className,
        event.target.dataset.taskId,
        event.target.dataset.id
    );

    const subTaskId = event.target.dataset.id;
    const taskId = event.target.dataset.taskId;

    if(event.target.classList.contains("deleteSubTaskButton")){
        await deleteSubTask(taskId, subTaskId);
    }

    if(event.target.classList.contains("updateSubTaskButton")){
        const labelToInput =
            document.querySelector(`[data-subtask-name="${subTaskId}"]`);

        labelToInput.innerHTML = `
            <form
                class="updateSubTaskForm"
                data-task-id="${taskId}"
                data-subtask-id="${subTaskId}"
            >
                <input
                    type="text"
                    id="subTaskName-${subTaskId}"
                    class="form-control form-control-sm"
                    placeholder="サブタスク名を入力"
                    required
                >

                <div class="d-flex gap-2">
                    <button
                        type="submit"
                        class="btn btn-warning w-100 mt-1 subtask-action-btn"
                    >
                        登録完了
                    </button>

                    <button
                        type="button"
                        class="btn btn-secondary w-100 mt-1 subtask-action-btn cancelUpdateSubTaskButton"
                        data-task-id="${taskId}"
                    >
                        キャンセル
                    </button>
                </div>
            </form>
        `;
    }

    if (event.target.classList.contains("addSubTaskButton")){
        const addArea = document.getElementById(`subTaskAdd-${taskId}`);

        addArea.innerHTML = `
            <form class="addSubTaskForm" data-task-id="${taskId}">
                <input
                    type="text"
                    id="newSubTaskName-${taskId}"
                    class="form-control form-control-sm subtask-add-input"
                    placeholder="サブタスク名を入力"
                    required
                >

                <div class="d-flex gap-2">
                    <button
                        type="submit"
                        class="btn btn-success w-100 mt-1 subtask-action-btn"
                    >
                        登録完了
                    </button>

                    <button
                        type="button"
                        class="btn btn-secondary w-100 mt-1 subtask-action-btn cancelAddSubTaskButton"
                        data-task-id="${taskId}"
                    >
                        キャンセル
                    </button>
                </div>
            </form>
        `;
    }
    if (event.target.classList.contains("cancelUpdateSubTaskButton")) {
        await fetchAndDisplaySubTasks(taskId);
        return;
    }

    if (event.target.classList.contains("cancelAddSubTaskButton")) {
        document.getElementById(`subTaskAdd-${taskId}`).innerHTML = "";
        return;
    }
});

document.getElementById("taskList").addEventListener("submit", async function(event) {

    if (
        !event.target.classList.contains("addSubTaskForm") &&
        !event.target.classList.contains("updateSubTaskForm")
    ) {
        return;
    }

    event.preventDefault();

    if (event.target.classList.contains("addSubTaskForm")) {
        const taskId = event.target.dataset.taskId;

        const addingSubtaskName =
            document.getElementById(`newSubTaskName-${taskId}`).value;
        
        const success = await addSubTask(taskId, addingSubtaskName);

        if (success) {
            document.getElementById(`subTaskAdd-${taskId}`).innerHTML = "";
        }
    }

    if (event.target.classList.contains("updateSubTaskForm")) {
        const taskId = event.target.dataset.taskId;
        const subTaskId = event.target.dataset.subtaskId;

        const changingSubtaskName =
            document.getElementById(`subTaskName-${subTaskId}`).value;

        const changingIsComplete =
            document.getElementById(`isComplete-${subTaskId}`).checked;

        await updateSubTask(
            taskId,
            subTaskId,
            changingSubtaskName,
            changingIsComplete
        );
    }
});

async function deleteSubTask(taskId, subTaskId) {

    const token = getToken();

    try{
        const response = await send_request({
            method: 'DELETE',
            token: token,
            url: `${apiUrl}/${taskId}/subtasks/${subTaskId}`,
        });

        if (response.ok) {
            await fetchAndDisplaySubTasks(taskId);
            await refreshTask(taskId);
        }else if(response.status === 401) {
            alert("認証エラーが発生しました。再度ログインしてください。");
            localStorage.removeItem('token');
            window.location.href = "./login.html";
        } else {
            const err = await response.json();
            alert(err.detail || "サブタスクの削除に失敗しました");
        }
    } catch (error) {
        console.error('サブタスク削除中にエラーが発生しました', error);
    }
}


async function fetchAndDisplaySubTasks(taskId) {

    const token = getToken();

    try {
        const response = await send_request({
            method: 'GET',
            token: token,
            url: `${apiUrl}/${taskId}/subtasks`,
        });

        const subTasks = await response.json();

        if (response.ok) {
            displaySubTasks(taskId, subTasks);
        }else if(response.status === 401) {
            alert("認証エラーが発生しました。再度ログインしてください。");
            localStorage.removeItem('token');
            window.location.href = "./login.html";
        } else {
            console.error("サブタスク取得失敗:", subTasks);
        }
    } catch (error) {
        console.error('サブタスク取得中にエラーが発生しました', error);
    }
}

function displaySubTasks(taskId, subTasks){
    const list = document.getElementById(`subTaskList-${taskId}`);
    list.innerHTML = '';

    let htmlContent = '';

    subTasks.forEach(function(subTask){
        htmlContent += `
            <div id="subtask-${subTask.subtask_id}">
                <div class="d-flex w-100 align-items-center">
                    <div class="d-flex gap-2 pe-3">
                        <div class="form-check form-switch d-flex align-items-center gap-2">
                            <input
                                class="form-check-input subTaskCheck"
                                type="checkbox"
                                role="switch"
                                id="isComplete-${subTask.subtask_id}"
                                data-id="${subTask.subtask_id}"
                                data-task-id="${taskId}"
                                data-name="${subTask.subtask_name}"
                                ${subTask.is_complete ? 'checked' : ''}
                            >
                            <label
                                class="form-check-label" style="width: 10rem;"
                                for="isComplete-${subTask.subtask_id}"
                                data-subtask-name="${subTask.subtask_id}"
                            >
                                ${subTask.subtask_name}
                            </label>
                        </div>
                    </div>
                    <div class="d-flex ms-auto gap-2 pe-3">
                        <button type="button" class="btn btn-danger btn-sm subtask-action-btn deleteSubTaskButton"
                            data-id="${subTask.subtask_id}"
                            data-task-id="${taskId}"
                        >
                            削除
                        </button>
                        
                        <button type="button" class="btn btn-warning btn-sm subtask-action-btn updateSubTaskButton"
                            data-id="${subTask.subtask_id}"
                            data-task-id="${taskId}"
                        >
                            編集
                        </button>
                    </div>
                </div>
            </div>
        `;
    });

    list.innerHTML = htmlContent;
}
