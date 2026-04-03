const loginForm = document.getElementById('login-form');

loginForm.addEventListener('submit', async(e) => {
    e.preventDefault();

    const btn = document.getElementById('SigninBtn');
    btn.textContent ="Logging in...";
    btn.disabled = true;


    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch("https://medical-report-analyzer-ai-production.up.railway.app/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            "email": email,
            "password": password
        })
    });

    btn.textContent = "Sign In";
    btn.disabled = false;

    const data = await response.json();

    if (response.ok ) {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        alert("Logged In Successfully!");
        window.location.href = "dashboard.html";

    } else {
        alert(data.error);
    }
});
