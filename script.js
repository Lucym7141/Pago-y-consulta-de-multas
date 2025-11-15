// scripts.js - Funcionalidad para MultasClear

// Verificar si el usuario está logueado
function checkAuth() {
    const user = localStorage.getItem('currentUser');
    if (user && window.location.pathname.includes('login.html')) {
        window.location.href = 'dashboard.html';
    }
    return user ? JSON.parse(user) : null;
}

// Mostrar mensajes
function showMessage(message, type = 'error') {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.textContent = message;
        messageDiv.className = `message ${type}`;
        setTimeout(() => {
            messageDiv.textContent = '';
            messageDiv.className = 'message';
        }, 5000);
    }
}

// Manejo del formulario de login
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    
    // Login Form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Validación básica
            if (!email || !password) {
                showMessage('Por favor, completa todos los campos');
                return;
            }
            
            // Obtener usuarios del localStorage
            const users = JSON.parse(localStorage.getItem('users')) || [];
            
            // Buscar usuario
            const user = users.find(u => u.email === email && u.password === password);
            
            if (user) {
                // Guardar sesión
                localStorage.setItem('currentUser', JSON.stringify(user));
                showMessage('Inicio de sesión exitoso. Redirigiendo...', 'success');
                
                // Redirigir después de un breve delay
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);
            } else {
                showMessage('Credenciales incorrectas. Por favor, verifica tu email y contraseña.');
            }
        });
    }
    
    // Signup Form
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            // Validaciones
            if (!name || !email || !password || !confirmPassword) {
                showMessage('Por favor, completa todos los campos');
                return;
            }
            
            if (password !== confirmPassword) {
                showMessage('Las contraseñas no coinciden');
                return;
            }
            
            if (password.length < 6) {
                showMessage('La contraseña debe tener al menos 6 caracteres');
                return;
            }
            
            // Obtener usuarios del localStorage
            const users = JSON.parse(localStorage.getItem('users')) || [];
            
            // Verificar si el usuario ya existe
            if (users.find(u => u.email === email)) {
                showMessage('Este email ya está registrado');
                return;
            }
            
            // Crear nuevo usuario
            const newUser = {
                id: Date.now(),
                name,
                email,
                password
            };
            
            // Guardar usuario
            users.push(newUser);
            localStorage.setItem('users', JSON.stringify(users));
            
            showMessage('Registro exitoso. Redirigiendo al login...', 'success');
            
            // Redirigir después de un breve delay
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1500);
        });
    }
    
    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            localStorage.removeItem('currentUser');
            window.location.href = 'index.html';
        });
    }
});