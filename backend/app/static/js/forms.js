/** Diálogo de formulario reutilizable (<dialog>) con envío asíncrono y errores en línea. */
export function openFormDialog({ title, submitLabel = 'Guardar', fields, onSubmit }) {
  return new Promise((resolve) => {
    const dialog = document.createElement('dialog');
    dialog.className = 'glass-card';
    dialog.style.cssText =
      'width:min(520px,calc(100% - 32px));padding:var(--space-6);border:1px solid var(--outline-variant);' +
      'border-radius:var(--radius-md);max-height:90vh;overflow:auto;';

    const form = document.createElement('form');
    form.style.cssText = 'display:flex;flex-direction:column;gap:var(--space-3);';
    const heading = document.createElement('h2');
    heading.className = 'headline-md';
    heading.style.margin = '0';
    heading.textContent = title;
    form.appendChild(heading);

    fields.forEach((field) => {
      const wrapper = document.createElement('div');
      const label = document.createElement('label');
      label.className = 'label-base';
      label.htmlFor = `dlg-${field.name}`;
      label.textContent = field.label;
      let input;
      if (field.type === 'textarea') {
        input = document.createElement('textarea');
        input.rows = 4;
      } else if (field.type === 'select') {
        input = document.createElement('select');
        (field.options || []).forEach(({ value, label: text }) => {
          const option = document.createElement('option');
          option.value = value;
          option.textContent = text;
          input.appendChild(option);
        });
      } else {
        input = document.createElement('input');
        input.type = field.type || 'text';
        if (field.min !== undefined) input.min = field.min;
      }
      input.className = 'input-base';
      input.id = `dlg-${field.name}`;
      input.name = field.name;
      input.required = Boolean(field.required);
      if (field.placeholder) input.placeholder = field.placeholder;
      if (field.value !== undefined) input.value = field.value;
      wrapper.append(label, input);
      form.appendChild(wrapper);
    });

    const error = document.createElement('p');
    error.setAttribute('role', 'alert');
    error.className = 'body-md';
    error.style.cssText = 'margin:0;color:var(--error);min-height:1em;';
    const actions = document.createElement('div');
    actions.style.cssText = 'display:flex;gap:var(--space-3);justify-content:flex-end;';
    const cancel = document.createElement('button');
    cancel.type = 'button';
    cancel.className = 'btn btn-outline label-caps';
    cancel.textContent = 'Cancelar';
    const submit = document.createElement('button');
    submit.type = 'submit';
    submit.className = 'btn btn-primary label-caps';
    submit.textContent = submitLabel;
    actions.append(cancel, submit);
    form.append(error, actions);
    dialog.appendChild(form);
    document.body.appendChild(dialog);

    let result = null;
    const close = () => dialog.close();
    cancel.addEventListener('click', close);
    dialog.addEventListener('close', () => {
      dialog.remove();
      resolve(result);
    });
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const values = Object.fromEntries(new FormData(form).entries());
      submit.disabled = true;
      error.textContent = '';
      try {
        result = (await onSubmit(values)) ?? true;
        close();
      } catch (failure) {
        error.textContent = failure.message;
        submit.disabled = false;
      }
    });
    dialog.showModal();
  });
}
