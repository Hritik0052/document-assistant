document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.querySelector('[data-dropzone]');
  const input = document.querySelector('[data-dropzone-input]');
  const label = document.querySelector('[data-dropzone-label]');

  if (dropzone && input) {
    const highlight = (on) => dropzone.classList.toggle('is-dragover', on);

    dropzone.addEventListener('click', () => input.click());
    dropzone.addEventListener('dragover', (event) => {
      event.preventDefault();
      highlight(true);
    });
    dropzone.addEventListener('dragleave', () => highlight(false));
    dropzone.addEventListener('drop', (event) => {
      event.preventDefault();
      highlight(false);
      if (event.dataTransfer.files.length) {
        input.files = event.dataTransfer.files;
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
    input.addEventListener('change', () => {
      if (label && input.files[0]) {
        label.textContent = input.files[0].name;
      }
    });
  }

  document.body.addEventListener('htmx:afterSwap', (event) => {
    if (event.detail.target && event.detail.target.id === 'message-list') {
      event.detail.target.scrollTop = event.detail.target.scrollHeight;
    }
  });

  const thread = document.getElementById('message-list');
  if (thread) {
    thread.scrollTop = thread.scrollHeight;
  }
});

document.body.addEventListener('htmx:configRequest', (event) => {
  const csrf = document.querySelector('[name=csrfmiddlewaretoken]');
  if (csrf) {
    event.detail.headers['X-CSRFToken'] = csrf.value;
  }
});
