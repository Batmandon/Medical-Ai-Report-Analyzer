const registerForm = document.getElementById('register-form');

registerForm.addEventListener('submit', async(e) => {
    e.preventDefault();

    const btn = document.getElementById('SignupBtn');
    btn.textContent ="Registering...";
    btn.disabled = true;

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch("https://medical-report-analyzer-ai-production.up.railway.app/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            "name": name,
            "email": email,
            "password": password
        })
    });

    btn.textContent = "Sign Up";
    btn.disabled = false;

    const data = await response.json();
    if (response.ok ) {
        alert("Registered Successfully!");
        window.location.href = "login.html";
    } else {
        alert(data.error);
    }
});
