(function () {
  var COLLAPSE_HEIGHT = 80; // px、約3行分

  function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
  }

  function initTextarea(el) {
    if (el.dataset.initialized) return;
    el.dataset.initialized = '1';

    el.style.height = 'auto';
    var fullHeight = el.scrollHeight;

    if (fullHeight <= COLLAPSE_HEIGHT) {
      // 短いコンテンツ：折りたたみ不要
      el.style.height = fullHeight + 'px';
      el.addEventListener('input', function () { autoResize(el); });
      return;
    }

    // 長いコンテンツ：折りたたみトグルを追加
    var label = el.parentNode; // <label>
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'toggle-memo';
    label.parentNode.insertBefore(btn, label.nextSibling);

    function collapse() {
      el.style.height = COLLAPSE_HEIGHT + 'px';
      el.style.overflow = 'hidden';
      btn.textContent = '全文表示';
      btn.dataset.expanded = '';
    }

    function expand() {
      el.style.overflow = 'hidden';
      autoResize(el);
      btn.textContent = '折りたたむ';
      btn.dataset.expanded = '1';
    }

    btn.addEventListener('click', function () {
      btn.dataset.expanded ? collapse() : expand();
    });

    el.addEventListener('input', function () {
      if (btn.dataset.expanded) autoResize(el);
    });

    collapse(); // デフォルトは折りたたみ
  }

  function initTextareas(root) {
    root.querySelectorAll('textarea').forEach(initTextarea);
  }

  initTextareas(document);

  document.addEventListener('htmx:afterSettle', function (e) {
    initTextareas(e.detail.elt);
  });
})();
