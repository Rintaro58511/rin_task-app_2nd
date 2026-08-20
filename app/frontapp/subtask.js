const taskList = document.getElementById("taskList");
const createSubTaskForm = document.getElementById("createSubTaskForm");

taskList.addEventListener("click", function (event) {
    if (!event.target.classList.contains("addSubTaskButton")){
        return;
    }

    selectedTaskId = event.target.dataset.id;

    createSubTaskForm.innerHTML = `
        <div class="card mb-3" style="width: 20rem; border-color: green;">
            <div class="card-body">
                <div class="mb-3">
                    <label for="subTaskName" class="form-label">
                        サブタスク名
                    </label>

                    <input
                        type="text"
                        id="subTaskName"
                        class="form-control"
                        placeholder="サブタスク名を入力"
                        required
                    >
                </div>

                <button type="submit" class="btn btn-success w-100 mt-2">
                    登録完了
                </button>

                <button
                    type="button"
                    class="btn btn-secondary w-100 mt-1"
                    id="cancelSubTaskButton"
                >
                    キャンセル
                </button>
            </div>
        </div>
    `;
});


createSubTaskForm.addEventListener("submit", async function (event){
    event.preventDefault();

    const subTaskData = {
        subtask_name: document.getElementById("subTaskName").value,
        is_complete: false,
    };

    await addSubTask(subTaskData);
});


createSubTaskForm.addEventListener("click", function (event){
    if (!event.target.matches("#cancelSubTaskButton")) {
        return;
    }

    createSubTaskForm.innerHTML = "";
    selectedTaskId = null;
});


async function addSubTask(subTask){
    
    const token = getToken();

    try {
        const response = await send_request({
            method: "POST",
            token: token,
            url: `${apiUrl}/${selectedTaskId}/subtask`,
            body: subTask,
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message || "サブタスクの追加が完了しました");

            createSubTaskForm.innerHTML = "";
            selectedTaskId = null;

            await fetchAndDisplayTasks();
        }else if(response.status === 401) {
            alert("認証エラーが発生しました。再度ログインしてください。");
            localStorage.removeItem('token');
            window.location.href = "./login.html";
        } else {
            alert(data.detail || "サブタスクの追加に失敗しました");
        }
    } catch (error) {
        console.error("サブタスク追加中にエラーが発生しました", error);
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
            alert(err.detail || "タスクの更新に失敗しました");
        }
    } catch (error) {
        console.error('タスク更新中にエラーが発生しました', error);
    }
}

document.getElementById("taskList").addEventListener("click", async function(event){

    if(!event.target.classList.contains("deleteSubTaskButton") && !event.target.classList.contains("updateSubTaskButton") && !event.target.classList.contains("updateCompleteButton") && !event.target.classList.contains("cancelSubTaskButton")){
        return;
    }

    const subTaskId = event.target.dataset.id;
    const taskId = event.target.dataset.taskId;

    if(event.target.classList.contains("deleteSubTaskButton")){
        await deleteSubTask(taskId, subTaskId);
    }

    if(event.target.classList.contains("updateSubTaskButton")){
        const labelToInput = document.querySelector(`[data-subtask-name="${subTaskId}"]`)
        labelToInput.innerHTML = `<input
                                        type="text"
                                        id="subTaskName-${subTaskId}"
                                        class="form-control"
                                        placeholder="サブタスク名を入力"
                                        required
                                    >
                                    <button
                                        type="button"
                                        class="btn btn-warning w-100 mt-2 updateCompleteButton"
                                        data-id = "${subTaskId}"
                                        data-task-id = "${taskId}"
                                    >
                                        登録完了
                                    </button>

                                    <button
                                        type="button"
                                        class="btn btn-secondary w-100 mt-1 cancelSubTaskButton"
                                        data-task-id = "${taskId}"
                                    >
                                        キャンセル
                                    </button>`
    }

    if(event.target.classList.contains("updateCompleteButton")){

        const changingSubtaskName = document.getElementById(`subTaskName-${subTaskId}`).value;
        const changingIsComplete = document.getElementById(`isComplete-${subTaskId}`).checked;

        await updateSubTask(taskId, subTaskId, changingSubtaskName, changingIsComplete);
    }

    if(event.target.classList.contains("cancelSubTaskButton")){

        await fetchAndDisplaySubTasks(taskId);
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
                        <div class="form-check form-switch">
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
                                class="form-check-label"
                                for="isComplete-${subTask.subtask_id}"
                                data-subtask-name="${subTask.subtask_id}"
                            >
                                ${subTask.subtask_name}
                            </label>
                        </div>
                    </div>
                    <div class="d-flex ms-auto gap-2 pe-3">
                        <button type="button" class="btn btn-danger btn-sm deleteSubTaskButton"
                            data-id="${subTask.subtask_id}"
                            data-task-id="${taskId}"
                        >
                            削除
                        </button>
                        
                        <button type="button" class="btn btn-warning btn-sm updateSubTaskButton"
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
