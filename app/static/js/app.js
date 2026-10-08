// Demande une confirmation avant les actions destructrices (formulaires avec data-confirm).
document.addEventListener("submit", function (event) {
  const message = event.target.dataset ? event.target.dataset.confirm : null;
  if (message && !window.confirm(message)) {
    event.preventDefault();
  }
});
