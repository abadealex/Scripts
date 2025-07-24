document.addEventListener('DOMContentLoaded', () => {
  const tabs = document.querySelectorAll('.tab');
  const panes = document.querySelectorAll('.tab-pane');

  function activateTab(tab) {
    tabs.forEach(t => {
      t.classList.remove('active');
      t.setAttribute('aria-selected', 'false');
      t.setAttribute('tabindex', '-1');
    });
    panes.forEach(pane => {
      pane.classList.remove('active');
      pane.setAttribute('hidden', '');
    });

    tab.classList.add('active');
    tab.setAttribute('aria-selected', 'true');
    tab.setAttribute('tabindex', '0');

    const targetId = tab.getAttribute('data-target');
    const targetPane = document.getElementById(targetId);
    if (targetPane) {
      targetPane.classList.add('active');
      targetPane.removeAttribute('hidden');
    }

    tab.focus();
  }

  tabs.forEach((tab, index) => {
    // Click event
    tab.addEventListener('click', () => activateTab(tab));

    // Keyboard navigation: left/right arrows
    tab.addEventListener('keydown', (e) => {
      let newIndex = null;
      if (e.key === 'ArrowRight') {
        newIndex = (index + 1) % tabs.length;
      } else if (e.key === 'ArrowLeft') {
        newIndex = (index - 1 + tabs.length) % tabs.length;
      } else if (e.key === 'Home') {
        newIndex = 0;
      } else if (e.key === 'End') {
        newIndex = tabs.length - 1;
      }

      if (newIndex !== null) {
        e.preventDefault();
        activateTab(tabs[newIndex]);
      }
    });
  });

  // Show loading indicator for iframes
  document.querySelectorAll('.iframe-wrapper iframe').forEach(iframe => {
    const loading = iframe.nextElementSibling;
    if (loading && loading.classList.contains('loading-indicator')) {
      loading.style.display = 'block';
      iframe.addEventListener('load', () => {
        loading.style.display = 'none';
      });
    }
  });
});
