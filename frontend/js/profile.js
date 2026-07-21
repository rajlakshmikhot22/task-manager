/**
 * profile.js — Profile view, avatar upload, password change.
 */

const Profile = (() => {

  async function load() {
    try {
      const user = await Api.getProfile();
      renderProfile(user);
    } catch (err) {
      Toast.show('Failed to load profile', 'error');
    }
  }

  function renderProfile(user) {
    document.getElementById('profile-fullname').textContent = user.full_name || user.username;
    document.getElementById('profile-email').textContent    = user.email;
    document.getElementById('profile-role').textContent     = user.role;

    // Fields
    document.getElementById('pf-fullname').value = user.full_name || '';
    document.getElementById('pf-username').value = user.username;
    document.getElementById('pf-bio').value      = user.bio || '';

    // Avatar display
    setAvatar('profile-avatar-display', user);
    setAvatar('sidebar-avatar',  user);
    setAvatar('topbar-avatar',   user);

    // Sidebar meta
    document.getElementById('sidebar-username').textContent = user.username;
    document.getElementById('sidebar-role').textContent     = user.role;
    document.getElementById('topbar-username').textContent  = user.username;
  }

  function setAvatar(elemId, user) {
    const el = document.getElementById(elemId);
    if (!el) return;
    if (user.avatar) {
      el.innerHTML = `<img src="${user.avatar}" alt="Avatar" />`;
    } else {
      el.innerHTML = (user.full_name || user.username || '?').charAt(0).toUpperCase();
    }
  }

  function init() {
    document.getElementById('btn-save-profile').addEventListener('click', saveProfile);
    document.getElementById('btn-change-pass').addEventListener('click', changePassword);
    document.getElementById('avatar-input').addEventListener('change', uploadAvatar);
  }

  async function saveProfile() {
    const payload = {
      full_name: document.getElementById('pf-fullname').value.trim() || null,
      username:  document.getElementById('pf-username').value.trim(),
      bio:       document.getElementById('pf-bio').value.trim() || null,
    };

    const btn = document.getElementById('btn-save-profile');
    btn.disabled = true; btn.textContent = 'Saving…';

    try {
      const user = await Api.updateProfile(payload);
      renderProfile(user);
      Toast.show('Profile updated!', 'success');
    } catch (err) {
      Toast.show(err.message, 'error');
    } finally {
      btn.disabled = false; btn.textContent = 'Save Changes';
    }
  }

  async function changePassword() {
    const current_password = document.getElementById('pf-cur-pass').value;
    const new_password     = document.getElementById('pf-new-pass').value;

    if (!current_password || !new_password) {
      Toast.show('Please fill in both password fields', 'error');
      return;
    }

    const btn = document.getElementById('btn-change-pass');
    btn.disabled = true; btn.textContent = 'Updating…';

    try {
      await Api.changePassword({ current_password, new_password });
      document.getElementById('pf-cur-pass').value = '';
      document.getElementById('pf-new-pass').value = '';
      Toast.show('Password updated successfully!', 'success');
    } catch (err) {
      Toast.show(err.message, 'error');
    } finally {
      btn.disabled = false; btn.textContent = 'Update Password';
    }
  }

  async function uploadAvatar(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      Toast.show('File is too large (max 5 MB)', 'error');
      return;
    }

    const form = new FormData();
    form.append('file', file);

    try {
      const user = await Api.uploadAvatar(form);
      renderProfile(user);
      Toast.show('Avatar updated!', 'success');
    } catch (err) {
      Toast.show(err.message, 'error');
    } finally {
      e.target.value = '';
    }
  }

  return { init, load };
})();
