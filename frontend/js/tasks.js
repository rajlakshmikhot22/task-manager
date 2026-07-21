/**
 * tasks.js — Task list, filtering, modal CRUD.
 */

const Tasks = (() => {
  let currentPage = 1;
  let totalPages  = 1;
  let searchTimer = null;

  // ── Init ─────────────────────────────────────────────────
  function init() {
    document.getElementById('btn-new-task').addEventListener('click', () => openModal());
    document.getElementById('btn-modal-save').addEventListener('click', saveTask);
    document.getElementById('btn-modal-cancel').addEventListener('click', closeModal);
    document.getElementById('modal-close').addEventListener('click', closeModal);
    document.getElementById('task-modal').addEventListener('click', e => {
      if (e.target === document.getElementById('task-modal')) closeModal();
    });

    // Filters
    document.getElementById('task-search').addEventListener('input', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => { currentPage = 1; load(); }, 350);
    });
    document.getElementById('filter-status').addEventListener('change',   () => { currentPage = 1; load(); });
    document.getElementById('filter-priority').addEventListener('change',  () => { currentPage = 1; load(); });
    document.getElementById('filter-sort').addEventListener('change',     () => { currentPage = 1; load(); });
    document.getElementById('btn-clear-filters').addEventListener('click', clearFilters);
  }

  function clearFilters() {
    document.getElementById('task-search').value   = '';
    document.getElementById('filter-status').value   = '';
    document.getElementById('filter-priority').value = '';
    document.getElementById('filter-sort').value     = 'created_at-desc';
    currentPage = 1;
    load();
  }

  // ── Load tasks ───────────────────────────────────────────
  async function load(page = currentPage) {
    currentPage = page;
    const [sort_by, sort_order] = (document.getElementById('filter-sort').value || 'created_at-desc').split('-');

    const params = {
      page: currentPage,
      size: 10,
      search:   document.getElementById('task-search').value.trim() || undefined,
      status:   document.getElementById('filter-status').value   || undefined,
      priority: document.getElementById('filter-priority').value || undefined,
      sort_by,
      sort_order,
    };

    try {
      const data = await Api.getTasks(params);
      totalPages = data.pages || 1;
      renderList(data.items, data.total);
      renderPagination();
    } catch (err) {
      Toast.show(err.message, 'error');
    }
  }

  // ── Render list ──────────────────────────────────────────
  function renderList(tasks, total) {
    const container = document.getElementById('task-list');
    if (!tasks.length) {
      container.innerHTML = `
        <div class="task-empty">
          <span class="task-empty-icon">📭</span>
          No tasks found. Create your first task!
        </div>`;
      return;
    }

    container.innerHTML = tasks.map(t => {
      const due      = t.due_date ? new Date(t.due_date) : null;
      const isOverdue = due && due < new Date() && t.status !== 'completed';
      const dueStr   = due ? due.toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' }) : '—';

      return `
      <div class="task-card priority-${t.priority} status-${t.status}" data-id="${t.id}">
        <div class="task-check ${t.status === 'completed' ? 'checked' : ''}"
             data-id="${t.id}" data-status="${t.status}" title="Toggle complete">
          ${t.status === 'completed' ? '✓' : ''}
        </div>
        <div class="task-body">
          <div class="task-title" title="${escHtml(t.title)}">${escHtml(t.title)}</div>
          ${t.description ? `<div class="task-desc" title="${escHtml(t.description)}">${escHtml(t.description)}</div>` : ''}
          <div class="task-meta">
            <span class="badge badge-${t.status}">${statusLabel(t.status)}</span>
            <span class="badge badge-${t.priority}">${capitalize(t.priority)}</span>
            <span class="task-due ${isOverdue ? 'overdue' : ''}">
              📅 ${dueStr}${isOverdue ? ' · Overdue' : ''}
            </span>
          </div>
        </div>
        <div class="task-actions">
          <button class="btn btn-ghost btn-sm" onclick="Tasks.openModal(${t.id})">✏ Edit</button>
          <button class="btn btn-danger btn-sm"  onclick="Tasks.deleteTask(${t.id})">🗑</button>
        </div>
      </div>`;
    }).join('');

    // Toggle complete via check circle
    container.querySelectorAll('.task-check').forEach(el => {
      el.addEventListener('click', async () => {
        const id     = parseInt(el.dataset.id);
        const status = el.dataset.status;
        const next   = status === 'completed' ? 'todo' : 'completed';
        try {
          await Api.updateTask(id, { status: next });
          load();
          Dashboard.load();
        } catch (err) {
          Toast.show(err.message, 'error');
        }
      });
    });
  }

  // ── Pagination ───────────────────────────────────────────
  function renderPagination() {
    const el = document.getElementById('task-pagination');
    if (totalPages <= 1) { el.innerHTML = ''; return; }

    let html = `<button class="btn btn-ghost btn-sm" ${currentPage === 1 ? 'disabled' : ''}
                  onclick="Tasks.load(${currentPage - 1})">‹ Prev</button>`;

    for (let i = 1; i <= totalPages; i++) {
      if (
        i === 1 || i === totalPages ||
        (i >= currentPage - 2 && i <= currentPage + 2)
      ) {
        html += `<button class="btn btn-ghost btn-sm ${i === currentPage ? 'active' : ''}"
                   onclick="Tasks.load(${i})">${i}</button>`;
      } else if (i === currentPage - 3 || i === currentPage + 3) {
        html += `<span style="color:var(--text-muted);padding:0 .3rem">…</span>`;
      }
    }

    html += `<button class="btn btn-ghost btn-sm" ${currentPage === totalPages ? 'disabled' : ''}
               onclick="Tasks.load(${currentPage + 1})">Next ›</button>`;
    el.innerHTML = html;
  }

  // ── Modal ────────────────────────────────────────────────
  async function openModal(taskId = null) {
    const modal = document.getElementById('task-modal');
    document.getElementById('modal-title').textContent = taskId ? 'Edit Task' : 'New Task';
    document.getElementById('modal-task-id').value     = taskId || '';

    if (taskId) {
      try {
        const task = await Api.getTasks({ page: 1, size: 1 });
        // Fetch single task
        const t = (await Api.getTasks({ page: 1, size: 200 })).items.find(x => x.id === taskId);
        if (t) populateModal(t);
      } catch {
        Toast.show('Could not load task details', 'error');
      }
    } else {
      resetModal();
    }
    modal.classList.remove('hidden');
  }

  function populateModal(t) {
    document.getElementById('task-title').value = t.title;
    document.getElementById('task-description').value = t.description || '';
    document.getElementById('task-priority').value = t.priority;
    document.getElementById('task-status').value   = t.status;
    if (t.due_date) {
      const d = new Date(t.due_date);
      const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000)
        .toISOString().slice(0, 16);
      document.getElementById('task-due-date').value = local;
    } else {
      document.getElementById('task-due-date').value = '';
    }
  }

  function resetModal() {
    document.getElementById('task-title').value       = '';
    document.getElementById('task-description').value = '';
    document.getElementById('task-priority').value    = 'medium';
    document.getElementById('task-status').value      = 'todo';
    document.getElementById('task-due-date').value    = '';
  }

  function closeModal() {
    document.getElementById('task-modal').classList.add('hidden');
  }

  async function saveTask() {
    const taskId = document.getElementById('modal-task-id').value;
    const title  = document.getElementById('task-title').value.trim();

    if (!title) { Toast.show('Title is required', 'error'); return; }

    const due_date = document.getElementById('task-due-date').value;
    const payload = {
      title,
      description: document.getElementById('task-description').value.trim() || null,
      priority:    document.getElementById('task-priority').value,
      status:      document.getElementById('task-status').value,
      due_date:    due_date ? new Date(due_date).toISOString() : null,
    };

    const btn = document.getElementById('btn-modal-save');
    btn.disabled = true; btn.textContent = 'Saving…';

    try {
      if (taskId) {
        await Api.updateTask(parseInt(taskId), payload);
        Toast.show('Task updated!', 'success');
      } else {
        await Api.createTask(payload);
        Toast.show('Task created!', 'success');
      }
      closeModal();
      load();
      Dashboard.load();
    } catch (err) {
      Toast.show(err.message, 'error');
    } finally {
      btn.disabled = false; btn.textContent = 'Save Task';
    }
  }

  async function deleteTask(taskId) {
    if (!confirm('Delete this task? This cannot be undone.')) return;
    try {
      await Api.deleteTask(taskId);
      Toast.show('Task deleted', 'info');
      load();
      Dashboard.load();
    } catch (err) {
      Toast.show(err.message, 'error');
    }
  }

  // ── Helpers ──────────────────────────────────────────────
  function escHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
  function statusLabel(s) {
    return { todo:'To Do', in_progress:'In Progress', completed:'Done', cancelled:'Cancelled' }[s] || s;
  }

  return { init, load, openModal, deleteTask };
})();
