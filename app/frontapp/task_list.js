const apiUrl = "http://localhost:8002/tasks"

const addButton = document.getElementById("addButton")
const createTaskForm = document.getElementById("createTaskForm")

addButton.addEventListener("click", function(){

    createTaskForm.innerHTML = `
        <div class="card mb-3" style="width: 20rem;">
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
                    <input type="text" id="taskDetail" class="form-control" placeholder="タスク詳細" required>
                </div>

                <div class="mb-3">
                    <label class="form-label">タスク進捗</label>
                    <div class="btn-group w-100" role="group">
                        <input type="radio" class="btn-check" name="taskStatus" id="statusTodo" value="TODO" checked>
                        <label class="btn btn-outline-primary" for="statusTodo">TODO</label>

                        <input type="radio" class="btn-check" name="taskStatus" id="statusProgress" value="IN_PROGRESS">
                        <label class="btn btn-outline-primary" for="statusProgress">IN_PROGRESS</label>

                        <input type="radio" class="btn-check" name="taskStatus" id="statusDone" value="DONE">
                        <label class="btn btn-outline-primary" for="statusDone">DONE</label>
                    </div>
                </div>

            <button type="submit" class="btn btn-primary w-100 mt-2">登録完了</button>
            </div>
        </div>
    `;
});

createTaskForm.addEventListener('submit', function(event){

    event.preventDefault();

    const taskName = document.getElementById('taskName').value;
    const taskDeadline = document.getElementById('taskDeadline').value;
    const taskDetail = document.getElementById('taskDetail').value;
    const selectedStatus = document.querySelector('input[name="taskStatus"]:checked').value;

    const taskData = {
        task_name: taskName,
        task_deadline: taskDeadline,
        task_detail: taskDetail,
        taskStatus: selectedStatus
    };

    addTask(taskData);
})

async function addTask(task){
    const token = localStorage.getItem('token');

    if (!token) {
        alert("ログインセッションが切れました。再ログインしてください。");
        window.location.href = "./login.html";
        return;
    }

    try{
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(task)
        });

        const data = await response.json()

        if(response.ok){
            alert(data.message || "タスクの追加が完了しました")
            createTaskForm.innerHTML = '';
            fetchAndDisplayTasks();
        }else if(response.status === 401){
            alert(tasks.detail || "認証エラーが発生しました。再度ログインしてください。");
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
    const token = localStorage.getItem('token');

    if(!token){
        alert("トークンが期限切れです。再度ログインして下さい。");
        window.location.href = "./login.html";
        return;
    }

    try{
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        tasks = await response.json();

        if(response.ok){
            display_tasks(tasks);
        }else{
            alert("トークンが期限切れです。再度ログインして下さい。");
            window.location.href = "./login.html";
            return;
        }
    }catch(error){
        console.error('タスク取得中にエラーが発生しました', error);
    }
}

function display_tasks(tasks){
    const list = document.getElementById('task_list');
    list.innerHTML = '';

    let htmlContent = '';
    tasks.forEach(function(task){
        htmlContent += `
            <div class="col">
                <div class="card mb-3" style="width: 18rem;">
                    <div class="card-body">
                        <h5 class="card-title">${task.task_name}</h5>
                        <h6 class="card-subtitle mb-2 text-body-secondary">締切: ${task.task_deadline}</h6>
                        <h6 class="card-subtitle mb-2 text-body-secondary">状態: ${task.taskStatus}</h6>
                        <p class="card-text">${task.task_detail}</p>
                    </div>
                </div>
            </div>
        `;
    });
    list.innerHTML = htmlContent;
}