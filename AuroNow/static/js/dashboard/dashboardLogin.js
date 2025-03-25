function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password');
    const showPasswordIcon = document.getElementById('showPasswordIcon');
    const hidePasswordIcon = document.getElementById('hidePasswordIcon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        showPasswordIcon.classList.add('hidden');
        hidePasswordIcon.classList.remove('hidden');
    } else {
        passwordInput.type = 'password';
        showPasswordIcon.classList.remove('hidden');
        hidePasswordIcon.classList.add('hidden');
    }
}