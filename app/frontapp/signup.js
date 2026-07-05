const apiUrl = "http://localhost:8002/user/signup"

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
    document.getElementById('name').value = '';
    document.getElementById('email').value = '';
    document.getElementById('password').value = '';
    document.getElementById('password_confirm').value = '';
}

document.getElementById('createUserForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    displayMessage([]);
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const passwordComfirm = document.getElementById('password_confirm').value;

    const errors = [];

    if(password != passwordComfirm){
        errors.push("パスワードと確認用パスワードが一致しません");
    }

    if(name.length < 3){
        errors.push("ユーザ名は3文字以上です");
    }

    if(password.length < 6){
        errors.push("パスワードは6文字以上です");
    }

    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    if (!emailRegex.test(email)) {
        errors.push("正しいメールアドレスの形式で入力してください");
    }

    if (errors.length > 0) {
        displayMessage(errors);
        return false;
    }

    const userData = {
        user_name: name,
        email: email,
        hashed_password: password
    };

    await signUpUser(userData);
})

async function signUpUser(user) {
    try{

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(user)
        });

        const data = await response.json();

        if(response.ok){
            alert(data.message || 'サインアップに成功しました');
            resetForm();
            return true;
        }else{
            alert(data.detail || 'サインアップに失敗しました')
            return false;
        }
    }catch(error){
        console.error('サインアップ中にエラーが発生しました', error);
        return false;
    }
}