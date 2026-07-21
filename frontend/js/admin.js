/**
 * admin.js — Admin panel: user management table.
 */

const Admin = (() => {
  let currentPage = 1;
  let totalPages  = 1;

  async function load(page = currentPage) {
    currentPage = page;
    try {
      const data = await Api.adminGetUsers(currentPage, 15);
      totalPages = data.pages || 1;
      renderStats(data);
      renderTable(data.items);
      renderPagination();
    } catch (err) {
      Toast.show(err.message, 'error');
    }
  }

  function renderStats(data) {
    document.getElementById('admin-user-count').textContent = data.total;
  }

  function renderTable(users) {
    const tbody = document.getElementById('admin-users-body');
    if (!users.length) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:2rem;color:var(--text-muted)">No users found</td></tr>';
      return;
    }

    tbody.innerHTML = users.map(u => {
      const joined = new Date(u.created_at).toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' });
      const activeClass = u.is_active ? 'badge-completed' : 'badge-cancelled';
      const activeLabel = u.is_active ? 'Active' : 'Inactive';
      const roleClass   = u.role === 'admin' ? 'badge-urgent' : 'badge-todo';

      return `
      <tr>
        <td>${u.id}</td>
        <td>
          <div style="display:flex;align-items:center;gap:.6rem">
            <div class="avatar-sm" style="width:28px;height:28px;font-size:.7rem">
              ${u.full_name ? u.full_name.charAt(0).toUpperCase() : u.username.charAt(0).toUpperCase()}
            </div>
            ${escHtml(u.username)}
          </div>
        </td>
        <td>${escHtml(u.email)}</td>
        <td><span class="badge ${roleClass}">${u.role}</span></td>
        <td><span class="badge ${activeClass}">${activeLabel}</span></td>
        <td>${joined}</td>
        <td>
          <div style="display:flex;gap:.4rem">
            <button class="btn btn-ghost btn-sm" onclick="Admin.toggleUser(${u.id})">
              ${u.is_active ? '🔒 Disable' : '🔓 Enable'}
            </button>
            <button class="btn btn-danger btn-sm" onclick="Admin.deleteUser(${u.id}, '${escHtml(u.username)}')">
              🗑 Delete
            </button>
          </div>
        </td>
      </tr>`;
    }).join('');
  }

  function renderPagination() {
    const el = document.getElementById('admin-user-pagination');
    if (totalPages <= 1) { el.innerHTML = ''; return; }

    let html = `<button class="btn btn-ghost btn-sm" ${currentPage === 1 ? 'disabled' : ''}
                  onclick="Admin.load(${currentPage - 1})">‹ Prev</button>`;
    for (let i = 1; i <= totalPages; i++) {
      html += `<button class="btn btn-ghost btn-sm ${i === currentPage ? 'active' : ''}"
                 onclick="Admin.load(${i})">${i}</button>`;
    }
    html += `<button class="btn btn-ghost btn-sm" ${currentPage === totalPages ? 'disabled' : ''}
               onclick="Admin.load(${currentPage + 1})">Next ›</button>`;
    el.innerHTML = html;
  }

  async function deleteUser(userId, username) {
    if (!confirm(`Delete user "${username}"? This will also delete all their tasks.`)) return;
    try {
      await Api.adminDeleteUser(userId);
      Toast.show(`User "${username}" deleted`, 'info');
      load();
    } catch (err) {
      Toast.show(err.message, 'error');
    }
  }

  async function toggleUser(userId) {
    try {
      const user = await Api.adminToggleUser(userId);
      Toast.show(`User "${user.username}" is now ${user.is_active ? 'active' : 'inactive'}`, 'info');
      load();
    } catch (err) {
      Toast.show(err.message, 'error');
    }
  }

  function escHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  return { load, deleteUser, toggleUser };
})();
