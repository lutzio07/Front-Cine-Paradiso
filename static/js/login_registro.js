//Obtencion de elementos por ID
const tabLogin = document.getElementById('tab-login');
const tabRegister = document.getElementById('tab-register');
const formLogin = document.getElementById('form-login');
const formRegister = document.getElementById('form-register');

//Alterna entre Login y Registro
if (tabLogin && tabRegister && formLogin && formRegister) {

  tabLogin.addEventListener('click', function() {
    formLogin.style.display = 'block';
    formRegister.style.display = 'none';
  });

  tabRegister.addEventListener('click', function() {
    formLogin.style.display = 'none';
    formRegister.style.display = 'block';
  });
}

//Muestra u oculta la contraseña
const botonesToggle = document.getElementsByClassName('toggle-password');

for (let i = 0; i < botonesToggle.length; i++) {
  const botonActual = botonesToggle[i];

  botonActual.addEventListener('click', function() {
    const contenedorPadre = botonActual.parentElement;
    const inputs = contenedorPadre.getElementsByTagName('input');

    if (inputs.length > 0) {
      const inputPassword = inputs[0];
      if (inputPassword.type === 'password') {
        inputPassword.type = 'text';
      } else {
        inputPassword.type = 'password';
      }
    }
  });
}

//Validacion de contraseñas al presionar el boton de registro
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
