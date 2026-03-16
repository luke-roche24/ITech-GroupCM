/* ── Auth Pages Shared JavaScript ──
   Used by: login.html, register.html, forgot_password.html
*/

/**
 * Toggle password visibility for a given input field.
 * Switches between 'password' and 'text' type,
 * and updates the eye icon accordingly.
 */
function togglePw(id, btn) {
    const input = document.getElementById(id);
    const icon = btn.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'bi bi-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'bi bi-eye';
    }
}

/**
 * Add real-time input validation styling.
 * Adds green border when input has content.
 */
function setupInputValidation(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.addEventListener('input', function () {
            this.classList.toggle('input-ok', this.value.length >= 1);
            this.classList.remove('input-err');
        });
    }
}

/**
 * Add loading spinner animation on form submit.
 * Disables the button and shows a spinner.
 */
function setupFormLoading(formId, btnId) {
    const form = document.getElementById(formId);
    const btn = document.getElementById(btnId);
    if (form && btn) {
        form.addEventListener('submit', function () {
            btn.classList.add('loading');
        });
    }
}