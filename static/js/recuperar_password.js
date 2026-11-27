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

const formResetPassword = document.getElementById('form-reset-password');

if (formResetPassword) {
  formResetPassword.addEventListener('submit', function(event) {
    const pass = document.getElementById('reset-password');
    const confirm = document.getElementById('reset-confirm');

    if (pass && confirm && pass.value !== confirm.value) {
      event.preventDefault();
      alert('Las contraseñas no coinciden.');
    }
  });
}