// Obtención de elementos por ID
const tabLogin = document.getElementById('tab-login');
const tabRegister = document.getElementById('tab-register');
const formLogin = document.getElementById('form-login');
const formRegister = document.getElementById('form-register');

// Alterna entre Login y Registro y mueve la línea roja indicadora
if (tabLogin && tabRegister && formLogin && formRegister) {

  tabLogin.addEventListener('click', function() {
    formLogin.style.display = 'block';
    formRegister.style.display = 'none';

    // Cambia la pestaña activa (mueve el indicador rojo)
    tabLogin.setAttribute('aria-selected', 'true');
    tabRegister.setAttribute('aria-selected', 'false');
  });

  tabRegister.addEventListener('click', function() {
    formLogin.style.display = 'none';
    formRegister.style.display = 'block';

    // Cambia la pestaña activa (mueve el indicador rojo)
    tabRegister.setAttribute('aria-selected', 'true');
    tabLogin.setAttribute('aria-selected', 'false');
  });
}

// Muestra u oculta la contraseña y conmuta el icono del ojo
const botonesToggle = document.getElementsByClassName('toggle-password');

for (let i = 0; i < botonesToggle.length; i++) {
  const botonActual = botonesToggle[i];

  botonActual.addEventListener('click', function() {
    const contenedorPadre = botonActual.parentElement;
    const inputs = contenedorPadre.getElementsByTagName('input');
    const icono = botonActual.querySelector('.material-symbols-outlined');

    if (inputs.length > 0) {
      const inputPassword = inputs[0];
      if (inputPassword.type === 'password') {
        inputPassword.type = 'text';
        if (icono) icono.textContent = 'visibility_off';
      } else {
        inputPassword.type = 'password';
        if (icono) icono.textContent = 'visibility';
      }
    }
  });
}

// Validación de contraseñas al presionar el botón de registro
const btnSubmitRegister = document.getElementById('btn-registrar');

if (btnSubmitRegister) {
  btnSubmitRegister.addEventListener('click', function() {
    const pass = document.getElementById('reg-password');
    const confirm = document.getElementById('reg-confirm');

    if (pass && confirm && pass.value !== confirm.value) {
      alert('Las contraseñas no coinciden.');
    }
  });
}
