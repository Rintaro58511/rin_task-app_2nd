const apiUrl = "http://localhost:8002/user/token"

function displayMessage(messages){
    const container = document.getElementById('errorContainer');

    if(!messages || messages.length === 0){
        container.innerHTML = '';
        return;
    }

    const errorList = Array.isArray(messages) ? messages : [messages];
    let html = `<div class="alert alert-danger p-2 small"><ul class="mb-0 ps-3">`;
    for (const msg of errorList) {
        html += `<li>${msg}</li>`;
    }
    html += `</ul></div>`;
    container.innerHTML = html;
}

function resetForm(){
    document.getElementById('email').value = '';
    document.getElementById('password').value = '';
}

document.getElementById('loginUserForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    displayMessage([]);

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const errors = [];

    if(password.length < 6){
        errors.push("パスワードは6文字以上です");
    }

    if (errors.length > 0) {
        displayMessage(errors);
        return false;
    }

    const userData = {
        email: email,
        password: password
    };

    const isSuccess = await loginUser(userData);

    if (isSuccess){
        localStorage.setItem('currentUser', email); 
    }
})

async function loginUser(user){
    try{
        const formData = new FormData();
        formData.append('username', user.email); 
        formData.append('password', user.password);
        const response = await fetch(apiUrl, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if(response.ok){
            localStorage.setItem('token', data.access_token);
            alert(data.message || 'ログインに成功しました');
            resetForm();
            return true;
        }else{
            alert(data.detail || 'ログインに失敗しました');
            return false;
        }
    }catch(error){
        console.error('ログイン中にエラーが発生しました', error);
        return false;
    }
}