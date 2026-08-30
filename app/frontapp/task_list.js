const apiUrl = `${API_BASE_URL}/tasks`;
let currentSort = localStorage.getItem('currentSort') || null;

function getCreateAndUpdateTime(){
    const now = new Date();

    const year = now.getFullYear();
    const month = (now.getMonth() + 1).toString().padStart(2, '0');
    const date = now.getDate().toString().padStart(2, '0');
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const seconds = now.getSeconds().toString().padStart(2, '0');

    return `${year}-${month}-${date}T${hours}:${minutes}:${seconds}`

}

function getToken(){
    const token = localStorage.getItem('token');

    if (!token) {
        alert("ログインセッションが切れました。再ログインしてください。");
        window.location.href = "./login.html";
        return;
    }

    return token;
}

async function send_request({method, token, url=apiUrl, body = null, headers = {}}){

    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...headers
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);
    return response;
}

const addButton = document.getElementById("addButton");
const createTaskForm = document.getElementById("createTaskForm");

addButton.addEventListener("click", function(){

    createTaskForm.innerHTML = `
        <div class="card mb-3" style="width: 20rem; border-color: green;">
            <div class="card-body">
                <div class="mb-3">
                    <label for="taskName" class="form-label">タスク名</label>
                    <input type="text" id="taskName" class="form-control" placeholder="タスク名を入力" required>
                </div>

                <div class="mb-3">
                    <label for="taskDeadline" class="form-label">タスク締切</label>
                    <input type="date" id="taskDeadline" class="form-control" placeholder="締切を入力" required>
                </div>

                <div class="mb-3">
                    <label for="taskDetail" class="form-label">タスク詳細</label>
                    <input type="text" id="taskDetail" class="form-control" placeholder="タスク詳細">
                </div>

                <div class="mb-3">
                    <label class="form-label">タスク進捗</label>
                    <div class="btn-group w-100" role="group">
                        <input type="radio" class="btn-check" name="taskStatus" id="statusTodo" value="TODO" checked>
                        <label class="btn btn-outline-success" for="statusTodo">TODO</label>

                        <input type="radio" class="btn-check" name="taskStatus" id="statusProgress" value="IN_PROGRESS">
                        <label class="btn btn-outline-success" for="statusProgress">IN_PROGRESS</label>

                        <input type="radio" class="btn-check" name="taskStatus" id="statusDone" value="DONE">
                        <label class="btn btn-outline-success" for="statusDone">DONE</label>
                    </div>
                </div>

            <button type="submit" class="btn btn-success w-100 mt-2">登録完了</button>
            <button type="button" class="btn btn-secondary w-100 mt-1" onclick="document.getElementById('createTaskForm').innerHTML=''">キャンセル</button>
            </div>
        </div>
    `;
});

createTaskForm.addEventListener('submit', function(event){

    event.preventDefault();

    const taskData = {
        task_name: document.getElementById('taskName').value,
        task_deadline: document.getElementById('taskDeadline').value,
        task_detail: document.getElementById('taskDetail').value,
        task_status: {
            task_progress: document.querySelector('input[name="taskStatus"]:checked').value,
            progress_ratio: 0,
            progress_comment: ""
    }
    };

    addTask(taskData);
})

async function addTask(task){

    const token = getToken()

    try{
        const response = await send_request({
            method: 'POST',
            token: token,
            body: task
        });

        const data = await response.json()

        if(response.ok){
            alert(data.message || "タスクの追加が完了しました")
            createTaskForm.innerHTML = '';
            fetchAndDisplayTasks();
        }else if(response.status === 401){
            alert(data.detail || "認証エラーが発生しました。再度ログインしてください。");
            localStorage.removeItem('token');
            window.location.href = "./login.html";
        }else{
            alert(data.detail || "タスクの追加に失敗しました")
            return false
        }
    }catch(error){
        console.error('タスク追加中にエラーが発生しました', error);
        return false;
    }
}


document.addEventListener("DOMContentLoaded", fetchAndDisplayTasks);
async function fetchAndDisplayTasks(){

    const token = getToken()

    try{
        let requestUrl = apiUrl;
        if (currentSort) {
            requestUrl = `${apiUrl}?sort=${currentSort}`;
        }

        const response = await send_request({
            method: 'GET',
            token: token,
            url: requestUrl
        });

        const tasks = await response.json();

        if(response.ok){
            displayTasks(tasks);
        }else{
            alert("トークンが期限切れです。再度ログインして下さい。");
            window.location.href = "./login.html";
            return;
        }
    }catch(error){
        console.error('タスク取得中にエラーが発生しました', error);
    }
}

function displayTasks(tasks){

    const list = document.getElementById('taskList');
    list.innerHTML = '';

    let htmlContent = '';
    tasks.forEach(function(task){
        
        const formattedTime = task.changed_time 
            ? new Intl.DateTimeFormat('ja-JP', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            }).format(new Date(task.changed_time))
            : 'なし';
        htmlContent += `
            <div class="col" id="task-card-${task.task_id}">
                <div class="card mb-3 task-card">
                    <div class="card-body">
                        <div class="progress" role="progressbar" aria-label="Animated striped example" aria-valuemin="0" aria-valuemax="100">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: ${task.task_status.progress_ratio}%" data-task-bar="${task.task_id}"></div>
                        </div>
                        <h5 class="card-title mt-2">${task.task_name}</h5>
                        <h6 class="card-subtitle mb-2 text-body-secondary">締切: ${task.task_deadline}</h6>
                        <h6 class="card-subtitle mb-2 text-body-secondary" data-task-status="${task.task_id}">状態: ${task.task_status.task_progress}</h6>
                        <p class="card-text">${task.task_detail}</p>
                        <div id="subTaskList-${task.task_id}"></div>
                        <button type="button" class="btn btn-success w-100 mt-2 addSubTaskButton" data-id="${task.task_id}">サブタスクの追加</button>
                        <button type="button" class="btn btn-warning w-100 mt-2 updateButton" data-id="${task.task_id}">変更</button>
                        <button type="button" class="btn btn-danger w-100 mt-2 deleteButton" data-id="${task.task_id}">削除</button>
                        <h6 class="card-subtitle mt-2 text-body-secondary">変更点：${task.task_status.progress_comment}</h6>
                        <h6 class="card-subtitle mt-2 text-body-secondary">変更時間：${formattedTime}</h6>
                    </div>
                </div>
            </div>
        `;
    });
    list.innerHTML = htmlContent;
    tasks.forEach(function(task) {
        fetchAndDisplaySubTasks(task.task_id);
    });
}

document.getElementById('taskList').addEventListener("click", async function(event){

    if(!event.target.classList.contains('deleteButton') && !event.target.classList.contains('updateButton') && !event.target.classList.contains('addSubTaskButton')) return;

    const taskId = event.target.dataset.id;

    if(event.target.classList.contains('deleteButton')){
        deleteTask(taskId);
    }
    if(event.target.classList.contains('updateButton')){
        updateTask(taskId);
    }
});

async function deleteTask(taskId){

    const token = getToken();

    try{

        const response = await send_request({
            method: 'DELETE',
            token: token,
            url: `${apiUrl}/${taskId}`
        });

        if(response.ok){
            alert("タスクを削除しました");
            await fetchAndDisplayTasks();
        }else if(response.status === 401) {
            alert("認証エラーが発生しました。再度ログインしてください。");
            localStorage.removeItem('token');
            window.location.href = "./login.html";
        }else{
            alert("タスクの削除に失敗しました。");
        }
    }catch(error){
        console.error('タスク削除中にエラーが発生しました', error);
    }
}


async function updateTask(taskId){

    const token = getToken();

    try{
        const response_for_get = await send_request({
        method: 'GET',
        token: token,
        url: `${apiUrl}/${taskId}`
        });

        if(!response_for_get.ok) {
            alert("タスク情報の取得に失敗しました");
            return;
        }

        const etag = response_for_get.headers.get("ETag");
        const task = await response_for_get.json();
        
        const targetCard = document.getElementById(`task-card-${taskId}`);
        if (!targetCard) {
                return;
        }
        targetCard.innerHTML = `
        <div class="card mb-3 task-card">
            <div class="card-body">
                <form class="form-update">
                    <h5>タスクの編集</h5>
                    <input type="hidden" class="updateTaskId" value="${task.task_id}">
                    <input type="hidden" class="updateTaskEtag" value="${etag}">
                    
                    <div class="mb-3">
                        <label for="updateTaskName" class="form-label">タスク名</label>
                        <input type="text" class="updateTaskName form-control" value="${task.task_name}" required>
                    </div>

                    <div class="mb-3">
                        <label for="updateTaskDeadline" class="form-label">タスク締切</label>
                        <input type="date" class="updateTaskDeadline form-control" value="${task.task_deadline}" required>
                    </div>

                    <div class="mb-3">
                        <label for="updateTaskDetail" class="form-label">タスク詳細</label>
                        <input type="text" class="updateTaskDetail form-control" value="${task.task_detail}" required>
                    </div>

                    <div class="mb-3 updateTaskProgress">
                        <label class="form-label" for="taskProgress">タスク進捗</label>
                        <div class="btn-group w-100" role="group">
                            <input type="radio" class="btn-check" name="updateTaskStatus" id="statusTodo" value="TODO" ${task.task_status.task_progress === 'TODO' ? 'checked' : ''} onchange="toggleProgressInput(this)">
                            <label class="btn btn-outline-warning" for="statusTodo">TODO</label>

                            <input type="radio" class="btn-check" name="updateTaskStatus" id="statusProgress" value="IN_PROGRESS" ${task.task_status.task_progress === 'IN_PROGRESS' ? 'checked' : ''} onchange="toggleProgressInput(this)">
                            <label class="btn btn-outline-warning" for="statusProgress">IN_PROGRESS</label>

                            <input type="radio" class="btn-check" name="updateTaskStatus" id="statusDone" value="DONE" ${task.task_status.task_progress === 'DONE' ? 'checked' : ''} onchange="toggleProgressInput(this)">
                            <label class="btn btn-outline-warning" for="statusDone">DONE</label>
                        </div>
                        <div class="input-group mb-3">
                            <input type="number" class="progressRatio form-control" value="${task.task_status.progress_ratio}" min="0" max="100" step="1" required ${task.task_status.task_progress !== 'IN_PROGRESS' ? 'disabled' : ''}>
                            <span class="input-group-text">%</span>
                        </div>
                        <input type="text" class="progressComment form-control" value="${task.task_status.progress_comment}" ${task.task_status.task_progress !== 'IN_PROGRESS' ? 'disabled' : ''}>

                    </div>

                    <button type="submit" class="btn btn-warning w-100 mt-2">変更を保存</button>
                    <button type="button" class="btn btn-secondary w-100 mt-1" onclick="cancelUpdate('${task.task_id}')">キャンセル</button>
                </form>
            </div>
        </div>
        `
    }catch(error){
        console.error('タスク取得中にエラーが発生しました', error);
    }
}

document.getElementById('taskList').addEventListener('submit', async function(event) {

    if (!event.target.classList.contains('form-update')) {
        return;
    }

    event.preventDefault();

    const form = event.target;
    const taskId = form.querySelector('.updateTaskId').value;
    const etag = form.querySelector('.updateTaskEtag').value;
    const token = getToken();

    const taskData = {
    task_name: form.querySelector('.updateTaskName').value,
    task_deadline: form.querySelector('.updateTaskDeadline').value,
    task_detail: form.querySelector('.updateTaskDetail').value,
    task_status: {
        task_progress: form.querySelector('input[name="updateTaskStatus"]:checked').value,
        progress_ratio: form.querySelector('.progressRatio').value,
        progress_comment: form.querySelector('.progressComment').value 
        }
    };

    try {
        const response = await send_request({
            method: 'PUT',
            token: token,
            url: `${apiUrl}/${taskId}`,
            body: taskData,
            headers: {
                'If-Match': etag
            }
        });

        if (response.ok) {
            alert("タスクを更新しました");
            fetchAndDisplayTasks();
        }else if(response.status === 401) {
            alert("認証エラーが発生しました。再度ログインしてください。");
            localStorage.removeItem('token');
            window.location.href = "./login.html";
        } else if (response.status === 412) {
            alert("このタスクは他のユーザーによって更新されました。最新の情報を再取得してください。");
            fetchAndDisplayTasks();
        } else {
            const err = await response.json();
            alert(err.detail || "タスクの更新に失敗しました");
        }
    } catch (error) {
        console.error('タスク更新中にエラーが発生しました', error);
    }
});

function cancelUpdate() {
    fetchAndDisplayTasks();
}

const sortDeadline = document.getElementById('sortDeadline');
sortDeadline.addEventListener("click", async function(event){
    event.preventDefault();

    currentSort = "deadline";
    localStorage.setItem('currentSort', currentSort);

    const token = getToken();

    try{
        const response = await send_request({
            method: 'GET',
            token: token,
            url: `${apiUrl}?sort=${currentSort}`
        });

        if(response.ok){
            const sorted_tasks = await response.json();
            displayTasks(sorted_tasks);
        }else{
            const err = await response.json();
            alert(err.detail || "タスクの更新に失敗しました");
        }
    }catch(error){
        console.error('タスク並び替え中にエラーが発生しました', error);
    }
})

const sortStatus = document.getElementById('sortStatus');
sortStatus.addEventListener("click", async function(event){
    event.preventDefault();

    currentSort = "status";
    localStorage.setItem('currentSort', currentSort);

    const token = getToken();

    try{
        const response = await send_request({
            method: 'GET',
            token: token,
            url: `${apiUrl}?sort=${currentSort}`
        });

        if(response.ok){
            const sortedTasks = await response.json();
            displayTasks(sortedTasks);
        }else{
            const err = await response.json();
            alert(err.detail || "タスクの更新に失敗しました");
        }
    }catch(error){
        console.error('タスク並び替え中にエラーが発生しました', error);
    }
})

const searchForm = document.getElementById('searchForm');

searchForm.addEventListener("submit", async function(event){
    event.preventDefault();

    const token = getToken();

    const searchName = document.getElementById('searchName')

    try{
        const response = await send_request({
            method: 'GET',
            token: token,
            url: `${apiUrl}?search_name=${searchName.value}`
        });

        if(response.ok){
            const seachedtasks = await response.json();
            console.log("バックエンドからのレスポンス:", seachedtasks);
            displayTasks(seachedtasks);
        }else{
            const err = await response.json();
            alert(err.detail || "タスクの検索に失敗しました");
        }
    }catch(error){
        console.error('タスク検索中にエラーが発生しました', error);
    }
})

function toggleProgressInput(radio) {
    const form = radio.closest('.form-update');
    const selectedStatus = form.querySelector('input[name="updateTaskStatus"]:checked').value;
    const progressInput = form.querySelector('.progressRatio');
    const commentInput = form.querySelector('.progressComment');

    if (selectedStatus === 'IN_PROGRESS') {
        progressInput.disabled = false;
        commentInput.disabled = false;
    } else {
        progressInput.disabled = true;
        commentInput.disabled = true;
        
        if (selectedStatus === 'TODO') {
            progressInput.value = 0;
        } else if (selectedStatus === 'DONE') {
            progressInput.value = 100;
        }
    }
}

const profileButton = document.getElementById("profile");

profileButton.addEventListener('click', async function(event){
    event.preventDefault();

    const token = getToken();
    const response = await send_request({
            method: 'GET',
            token: token,
            url: 'https://d25ee7cqp3i4lf.cloudfront.net/user/me'
        });

    const profile = await response.json();
    alert(`${profile.message}\nユーザー名: ${profile.user.user_name}\nEmail: ${profile.user.email}`)

})

async function refreshTask(taskId){
    const token = getToken();

    try {
        const response = await send_request({
            method: 'GET',
            token: token,
            url: `${apiUrl}/${taskId}`,
        });

        if (response.ok) {
            const refreshTask = await response.json()
            console.log("refreshTask:", refreshTask.task_status.progress_ratio);
            const barWidth = document.querySelector(`[data-task-bar="${taskId}"]`)
            const changedStatus = document.querySelector(`[data-task-status="${taskId}"]`)
            barWidth.style.width = `${refreshTask.task_status.progress_ratio}%`
            changedStatus.textContent = `状態: ${refreshTask.task_status.task_progress}`
        } else {
            const err = await response.json();
            alert(err.detail || "タスクの更新に失敗しました");
        }
    } catch (error) {
        console.error('タスク更新中にエラーが発生しました', error);
    }
}