const botonReporte = document.getElementById('descargar-reporte');
const notificaciones = document.getElementById('dashboard-notificaciones');

function avisar(mensaje) {
  const aviso = document.createElement('div');
  aviso.className = 'dashboard-aviso';
  aviso.setAttribute('role', 'alert');
  const texto = document.createElement('span');
  texto.textContent = mensaje;
  const cerrar = document.createElement('button');
  cerrar.type = 'button';
  cerrar.setAttribute('aria-label', 'Cerrar notificación');
  cerrar.textContent = '×';
  cerrar.addEventListener('click', () => aviso.remove());
  aviso.append(texto, cerrar);
  notificaciones.append(aviso);
  setTimeout(() => aviso.remove(), 6000);
}

botonReporte.addEventListener('click', async () => {
  botonReporte.disabled = true;
  try {
    const respuesta = await fetch(botonReporte.dataset.url, {headers: {'Accept': 'application/pdf'}});
    const tipo = respuesta.headers.get('content-type') || '';
    if (!respuesta.ok || respuesta.redirected || !tipo.toLowerCase().startsWith('application/pdf')) {
      let mensaje = 'No se pudo descargar el reporte PDF.';
      if (respuesta.status === 401 || respuesta.status === 403 || respuesta.redirected || tipo.includes('text/html')) mensaje = 'Sesión expirada o sin permisos. Iniciá sesión nuevamente.';
      else if (tipo.includes('application/json')) mensaje = (await respuesta.json()).error || mensaje;
      throw new Error(mensaje);
    }
    const blob = await respuesta.blob();
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement('a');
    enlace.href = url;
    enlace.download = 'reporte-cine-paradiso.pdf';
    document.body.append(enlace);
    enlace.click();
    enlace.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (error) {
    avisar(error.message || 'No se pudo descargar el reporte PDF.');
  } finally {
    botonReporte.disabled = false;
  }
});

document.querySelectorAll('.bar-fill[data-width]').forEach(barra => {
  const porcentaje = Number(barra.dataset.width) || 0;
  barra.style.width = `${Math.max(0, Math.min(100, porcentaje))}%`;
});
