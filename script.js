// Navigation System
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
    window.scrollTo(0,0);
}

// Sign Up Logic
function toggleSignup() {
    const checkbox = document.getElementById('terms-box');
    const btn = document.getElementById('signup-btn');
    btn.disabled = !checkbox.checked;
}

// Login Logic
function handleLogin() {
    const user = document.getElementById('login-user').value;
    const pass = document.getElementById('login-pass').value;
    const errorMsg = document.getElementById('login-error');

    // Simple dummy check (Replace with real backend auth)
    if (user === "admin" && pass === "password") {
        errorMsg.style.display = 'none';
        showPage('dashboard');
    } else {
        errorMsg.style.display = 'block';
    }
}

// Dropdown/Feature constraints could be added here
// e.g., enabling Upload button only when Patient and Language are picked.