const apiUrl = "http://localhost:8002/user/signup"

function displayMessage(message){
    alert(message);
}

function resetForm(){
    document.getElementById('name').value = '';
    document.getElementById('password').value = '';
    document.getElementById('password_confirm').value = '';
}

document.getElementById('createUserForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const passwordComfirm = document.getElementById('password_confirm').value;

    if(password != passwordComfirm){
        displayMessage("パスワードと確認用パスワードが一致しません");
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
            displayMessage(data.message || 'サインアップに成功しました');
            resetForm();
            return true;
        }else{
            displayMessage(data.detail || 'サインアップに失敗しました')
            return false;
        }
    }catch(error){
        console.error('サインアップ中にエラーが発生しました', error);
        return false;
    }
}