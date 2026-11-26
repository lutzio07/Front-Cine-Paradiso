document.querySelectorAll('.bar-fill[data-width]').forEach(barra => {
  const porcentaje = Number(barra.dataset.width) || 0;
  barra.style.width = `${Math.max(0, Math.min(100, porcentaje))}%`;
});
