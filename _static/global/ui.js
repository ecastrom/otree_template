/* otree_template — shared UI helpers: clickable-scale completeness check + two-list drag ranking */
(function () {
  // ── Clickable scales: every .lk-row[data-field] must have a checked radio
  function validateRows(form) {
    var ok = true, first = null;
    form.querySelectorAll('.lk-row[data-field]').forEach(function (row) {
      var name = row.getAttribute('data-field');
      var checked = row.hasAttribute('data-dial')
        ? (form.querySelector('input[name="' + name + '"]').value !== '')
        : form.querySelector('input[name="' + name + '"]:checked');
      if (!checked) {
        ok = false;
        row.classList.add('lk-missing');
        if (!first) first = row;
      } else {
        row.classList.remove('lk-missing');
      }
    });
    return { ok: ok, first: first };
  }

  // ── Two-list ranking: items start in #poolId and must ALL be moved to
  //    #listId (drag, tap, or buttons). Hidden inputs id = prefix_key get
  //    the 1-based position in the ranked list; empty while in the pool.
  var rankLists = [];
  window.rankList = function (poolId, listId, prefix, firstLabelId) {
    var pool = document.getElementById(poolId);
    var list = document.getElementById(listId);
    if (!pool || !list) return;
    function refresh() {
      Array.prototype.forEach.call(pool.children, function (li) {
        li.querySelector('.rank-pos').textContent = '';
        var inp = document.getElementById(prefix + '_' + li.getAttribute('data-key'));
        if (inp) inp.value = '';
      });
      Array.prototype.forEach.call(list.children, function (li, i) {
        li.querySelector('.rank-pos').textContent = i + 1;
        var inp = document.getElementById(prefix + '_' + li.getAttribute('data-key'));
        if (inp) inp.value = i + 1;
      });
      pool.classList.toggle('rank-empty', pool.children.length === 0);
      list.classList.toggle('rank-empty', list.children.length === 0);
      var n = pool.children.length;
      var cnt = document.getElementById(poolId + '-count');
      if (cnt) cnt.textContent = n ? ('Faltan ' + n + ' por ordenar') : 'Todas ordenadas';
      if (firstLabelId) {
        var f = list.firstElementChild;
        var lab = document.getElementById(firstLabelId);
        if (lab) lab.textContent = f ? f.querySelector('.rank-name').textContent : '—';
      }
    }
    if (window.Sortable) {
      var opts = {
        group: 'rank-' + prefix,
        animation: 150,
        delay: 120,             // long-press to drag on touch, so the page still scrolls
        delayOnTouchOnly: true,
        onSort: refresh, onAdd: refresh, onRemove: refresh
      };
      Sortable.create(pool, opts);
      Sortable.create(list, opts);
    }
    // Tap / buttons fallback
    pool.addEventListener('click', function (e) {
      var li = e.target.closest('.rank-item');
      if (!li) return;
      list.appendChild(li);
      refresh();
    });
    list.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      var li = b.closest('.rank-item');
      if (b.classList.contains('up') && li.previousElementSibling) {
        list.insertBefore(li, li.previousElementSibling);
      } else if (b.classList.contains('down') && li.nextElementSibling) {
        list.insertBefore(li.nextElementSibling, li);
      } else if (b.classList.contains('out')) {
        pool.appendChild(li);
      }
      refresh();
    });
    refresh();
    rankLists.push({ pool: pool, list: list });
  };

  // ── Dial: a continuous 0-100 answer by moving a range input. The hidden
  //    field stays EMPTY until the participant moves the dial (or taps -/+),
  //    so the default position is never recorded as an answer.
  window.dial = function (name) {
    var range = document.getElementById(name + '-range');
    var hidden = document.getElementById('id_' + name);
    var disp = document.getElementById(name + '-display');
    if (!range || !hidden) return;
    var row = range.closest('.lk-row');
    function set(v) {
      v = Math.max(+range.min, Math.min(+range.max, v));
      range.value = v; hidden.value = v; disp.textContent = v;
      row.classList.add('dial-set'); row.classList.remove('lk-missing');
      var f = range.form, e = f && f.querySelector('.lk-error');
      if (e && !f.querySelector('.lk-missing')) e.style.display = 'none';
    }
    range.addEventListener('input', function () { set(+range.value); });
    range.addEventListener('change', function () { set(+range.value); });
    row.querySelectorAll('.dial-step').forEach(function (b) {
      b.addEventListener('click', function () {
        set((hidden.value === '' ? +range.value : +hidden.value) + (+b.getAttribute('data-step')));
      });
    });
  };

  document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('form');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      var ok = true, first = null;
      if (form.querySelector('.lk-row[data-field]')) {
        var r = validateRows(form);
        ok = r.ok; first = r.first;
      }
      rankLists.forEach(function (rl) {
        if (rl.pool.children.length > 0) {
          ok = false;
          rl.pool.classList.add('lk-missing');
          if (!first) first = rl.pool;
        } else {
          rl.pool.classList.remove('lk-missing');
        }
      });
      var err = form.querySelector('.lk-error');
      if (err) err.style.display = ok ? 'none' : 'block';
      if (!ok) {
        if (first) first.scrollIntoView({ behavior: 'smooth', block: 'center' });
        e.preventDefault();
        e.stopImmediatePropagation();
      }
    }, true);
    form.querySelectorAll('.lk-row input').forEach(function (inp) {
      inp.addEventListener('change', function () {
        inp.closest('.lk-row').classList.remove('lk-missing');
      });
    });
  });
})();
