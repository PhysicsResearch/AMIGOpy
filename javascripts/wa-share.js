(function() {
  // Don’t add twice
  if (document.getElementById('wa-share')) return;

  const url = encodeURIComponent(window.location.href);
  const title = encodeURIComponent(document.title);
  const text = `${title}%0A${url}`;
  const shareLink = `https://wa.me/?text=${text}`;

  const a = document.createElement('a');
  a.id = 'wa-share';
  a.href = shareLink;
  a.target = '_blank';
  a.rel = 'noopener';

  // WhatsApp SVG icon (no external deps)
  a.innerHTML = `
    <svg viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <path d="M19.11 17.05c-.28-.14-1.64-.81-1.89-.9-.25-.09-.43-.14-.62.14-.19.28-.72.9-.89 1.09-.16.19-.33.21-.61.07-.28-.14-1.19-.44-2.27-1.4-.84-.75-1.41-1.67-1.57-1.95-.16-.28-.02-.43.12-.57.12-.12.28-.33.42-.5.14-.16.19-.28.28-.47.09-.19.05-.35-.02-.5-.07-.14-.62-1.49-.85-2.04-.22-.53-.45-.46-.62-.46l-.53-.01c-.19 0-.5.07-.76.35-.26.28-.99.97-.99 2.36 0 1.39 1.02 2.73 1.16 2.92.14.19 2.01 3.06 4.86 4.29.68.29 1.22.46 1.64.59.69.22 1.32.19 1.82.12.56-.08 1.64-.67 1.87-1.32.23-.65.23-1.2.16-1.32-.07-.12-.25-.19-.53-.33zM16.04 3.2C9.42 3.2 4.04 8.57 4.04 15.2c0 2.66.87 5.12 2.34 7.12L4 28l5.86-2.31c1.93 1.27 4.24 2.01 6.74 2.01 6.62 0 12-5.38 12-12.01 0-6.62-5.38-11.99-12-11.99zm0 21.88c-2.38 0-4.6-.77-6.4-2.07l-.46-.33-3.46 1.36 1.28-3.57-.3-.49a10.34 10.34 0 0 1-1.57-5.57c0-5.72 4.66-10.37 10.37-10.37 5.72 0 10.37 4.64 10.37 10.37 0 5.72-4.66 10.37-10.37 10.37z"/>
    </svg>
  `;

  document.body.appendChild(a);
})();
