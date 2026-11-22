(function () {
    const form = document.getElementById('form-crear-sala');
    if (!form) {
        return;
    }

    const contenedor = document.getElementById('sala-filas');
    const agregar = document.getElementById('sala-agregar-fila');
    const total = document.getElementById('sala-capacidad-total');
    const error = document.getElementById('sala-error');

    function letraFila(indice) {
        let letra = '';
        let valor = indice + 1;
        while (valor > 0) {
            valor -= 1;
            letra = String.fromCharCode(65 + (valor % 26)) + letra;
            valor = Math.floor(valor / 26);
        }
        return letra;
    }

    function filas() {
        return Array.from(contenedor.querySelectorAll('.sala-fila'));
    }

    function actualizar() {
        const actuales = filas();
        let capacidad = 0;

        actuales.forEach((fila, indice) => {
            fila.querySelector('.sala-fila-titulo').textContent = `Fila ${letraFila(indice)}`;
            fila.querySelector('.sala-quitar-fila').hidden = actuales.length === 1;
            for (const input of fila.querySelectorAll('input')) {
                capacidad += Number(input.value) || 0;
            }
        });

        total.value = capacidad;
        agregar.disabled = actuales.length >= 40;
        if (!error.hidden) {
            error.hidden = true;
        }
    }

    agregar.addEventListener('click', () => {
        const actuales = filas();
        const anterior = actuales[actuales.length - 1];
        const nueva = anterior.cloneNode(true);
        const anteriores = anterior.querySelectorAll('input');
        nueva.querySelectorAll('input').forEach((input, indice) => {
            input.value = anteriores[indice].value;
        });
        contenedor.appendChild(nueva);
        actualizar();
    });

    contenedor.addEventListener('click', (evento) => {
        if (evento.target.closest('.sala-quitar-fila') && filas().length > 1) {
            evento.target.closest('.sala-fila').remove();
            actualizar();
        }
    });

    contenedor.addEventListener('input', actualizar);

    form.addEventListener('submit', (evento) => {
        let capacidad = 0;
        let mensaje = '';

        filas().forEach((fila, indice) => {
            if (mensaje) {
                return;
            }
            const valores = Array.from(fila.querySelectorAll('input'), input => Number(input.value));
            if (valores.some(valor => !Number.isInteger(valor) || valor < 0)) {
                mensaje = `Revisá las cantidades de la fila ${letraFila(indice)}.`;
                return;
            }
            const [izquierda, centro, derecha] = valores;
            if (izquierda > 5 || derecha > 5 || centro < 1 || izquierda + centro + derecha < 5) {
                mensaje = `La fila ${letraFila(indice)} necesita al menos 5 butacas, centro mayor a 0 y laterales de hasta 5.`;
            }
            capacidad += izquierda + centro + derecha;
        });

        if (!mensaje && capacidad > 200) {
            mensaje = 'La sala no puede superar las 200 butacas.';
        }

        if (mensaje) {
            evento.preventDefault();
            error.textContent = mensaje;
            error.hidden = false;
            error.scrollIntoView({ block: 'nearest' });
        }
    });

    actualizar();
})();
