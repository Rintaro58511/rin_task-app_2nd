const apiUrl = "http://localhost:8002/user/token"

function displayMessage(message){
    alert(message)
}

function resetForm(){
    document.getElementById('name').value = ''
    document.getElementById('password').value = ''
}

document.getElementById('loginUserForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const name = document.getElementById('name').value
    const password = document.getElementById('password').value

    const userData = {
        user_name : name,
        password: password
    }

    const isSuccess = await loginUser(userData);

    if (isSuccess){
        localStorage.setItem('currentUser', name); 
    }
})

async function loginUser(user){
    try{
        const formData = new FormData();
        formData.append('username', user.user_name); 
        formData.append('password', user.password);
        const response = await fetch(apiUrl, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if(response.ok){
            localStorage.setItem('token', data.access_token);
            displayMessage(data.message || 'ログインに成功しました');
            resetForm();
            return true;
        }else{
            displayMessage(data.detail || 'ログインに失敗しました')
            return false;
        }
    }catch(error){
        console.error('ログイン中にエラーが発生しました', error);
        return false;
    }
}