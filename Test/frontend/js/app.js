/* =================================================================
 *  User Management System — app.js
 *  Auto-detects backend API; falls back to mock data when offline.
 * ================================================================= */

(function () {
  'use strict';

  // ─── Constants ──────────────────────────────────────────────
  var API_BASE = 'http://localhost:8080/api/users';
  var API_TIMEOUT = 2000; // ms to wait before falling back to mock

  // ─── State ──────────────────────────────────────────────────
  var useApi = false;
  var totalRecords = 0;    // server-side total (API mode)
  var mockUsers = [];      // local store (mock mode)
  var nextMockId = 1;
  var currentPage = 1;
  var pageSize = 10;
  var searchKeyword = '';
  var editingUserId = null;
  var deleteTargetId = null;

  // ─── DOM refs ───────────────────────────────────────────────
  function $(sel) { return document.querySelector(sel); }
  var tableBody       = $('#tableBody');
  var pageInfo        = $('#pageInfo');
  var paginationCtls  = $('#paginationControls');
  var searchInput     = $('#searchInput');
  var pageSizeSelect  = $('#pageSizeSelect');
  var modeBadge       = $('#modeBadge');

  // ─── Seed data (mock mode only) ─────────────────────────────
  function createSeedUsers() {
    var names  = ['张三丰','李思思','王五','赵六','孙七','周八','吴九','郑十','钱十一','陈十二','刘十三','黄十四','林十五','何十六','马十七'];
    var phones = ['13800138001','13900139002','13700137003','13600136004','13500135005','13400134006','13300133007','13200132008','13100131009','15800158010','15900159011','18800188012','18600186013','17700177014','15500155015'];
    var now = Date.now();
    return names.map(function (name, i) {
      var d = new Date(now - (14 - i) * 86400000);
      var ts = d.getFullYear() + '-' +
        String(d.getMonth() + 1).padStart(2, '0') + '-' +
        String(d.getDate()).padStart(2, '0') + ' ' +
        String(d.getHours()).padStart(2, '0') + ':' +
        String(d.getMinutes()).padStart(2, '0') + ':' +
        String(d.getSeconds()).padStart(2, '0');
      return {
        id: i + 1,
        username: name,
        phone: phones[i],
        email: name.replace(/[三四五六七八九十]/g, '').toLowerCase() + (i + 1) + '@example.com',
        createTime: ts
      };
    });
  }

  // ─── Data layer ─────────────────────────────────────────────
  function fetchPage(page, size, keyword) {
    if (useApi) {
      var params = '?page=' + page + '&size=' + size;
      if (keyword) params += '&keyword=' + encodeURIComponent(keyword);
      return fetch(API_BASE + params)
        .then(function (r) { return r.json(); })
        .then(function (json) {
          // Backend returns Result<Page<User>>
          if (json.code === 200 && json.data) {
            totalRecords = json.data.total || 0;
            return json.data.records || [];
          }
          throw new Error(json.message || 'API error');
        });
    } else {
      // Mock: filter, paginate
      var filtered = mockUsers;
      if (keyword) {
        var kw = keyword.toLowerCase();
        filtered = mockUsers.filter(function (u) {
          return u.username.toLowerCase().indexOf(kw) !== -1 || u.phone.indexOf(kw) !== -1;
        });
      }
      totalRecords = filtered.length;
      var start = (page - 1) * size;
      return Promise.resolve(filtered.slice(start, start + size));
    }
  }

  function addUser(data, onSuccess, onError) {
    if (useApi) {
      return fetch(API_BASE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(function (r) { return r.json(); })
      .then(function (json) {
        if (json.code === 200) { onSuccess(); } else { onError(json.message); }
      })
      .catch(function () { onError('网络错误'); });
    } else {
      mockUsers.push({
        id: nextMockId++,
        username: data.username.trim(),
        phone: data.phone.trim(),
        email: data.email.trim() || '',
        createTime: fmtNow()
      });
      onSuccess();
      return Promise.resolve();
    }
  }

  function updateUser(id, data, onSuccess, onError) {
    if (useApi) {
      return fetch(API_BASE + '/' + id, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(function (r) { return r.json(); })
      .then(function (json) {
        if (json.code === 200) { onSuccess(); } else { onError(json.message); }
      })
      .catch(function () { onError('网络错误'); });
    } else {
      for (var i = 0; i < mockUsers.length; i++) {
        if (mockUsers[i].id === id) {
          mockUsers[i].username = data.username.trim();
          mockUsers[i].phone    = data.phone.trim();
          mockUsers[i].email    = data.email.trim() || '';
          onSuccess();
          return Promise.resolve();
        }
      }
      onError('用户不存在');
      return Promise.resolve();
    }
  }

  function deleteUser(id, onSuccess, onError) {
    if (useApi) {
      return fetch(API_BASE + '/' + id, { method: 'DELETE' })
        .then(function (r) { return r.json(); })
        .then(function (json) {
          if (json.code === 200) { onSuccess(); } else { onError(json.message); }
        })
        .catch(function () { onError('网络错误'); });
    } else {
      for (var i = 0; i < mockUsers.length; i++) {
        if (mockUsers[i].id === id) {
          mockUsers.splice(i, 1);
          onSuccess();
          return Promise.resolve();
        }
      }
      onError('用户不存在');
      return Promise.resolve();
    }
  }

  // ─── Render ─────────────────────────────────────────────────
  function fmtNow() {
    var n = new Date();
    return n.getFullYear() + '-' +
      String(n.getMonth() + 1).padStart(2, '0') + '-' +
      String(n.getDate()).padStart(2, '0') + ' ' +
      String(n.getHours()).padStart(2, '0') + ':' +
      String(n.getMinutes()).padStart(2, '0') + ':' +
      String(n.getSeconds()).padStart(2, '0');
  }

  function escHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function renderTable() {
    var totalPages = Math.max(1, Math.ceil(totalRecords / pageSize));

    fetchPage(currentPage, pageSize, searchKeyword).then(function (records) {
      if (records.length === 0) {
        tableBody.innerHTML = '<tr class="empty-row"><td colspan="6">暂无数据</td></tr>';
      } else {
        tableBody.innerHTML = records.map(function (u) {
          return '<tr>' +
            '<td>' + u.id + '</td>' +
            '<td>' + escHtml(u.username) + '</td>' +
            '<td>' + escHtml(u.phone) + '</td>' +
            '<td>' + escHtml(u.email || '-') + '</td>' +
            '<td>' + (u.createTime || '') + '</td>' +
            '<td><div class="action-cell">' +
              '<button class="btn btn-outline btn-sm" data-edit="' + u.id + '">编辑</button>' +
              '<button class="btn btn-danger btn-sm" data-delete="' + u.id + '">删除</button>' +
            '</div></td>' +
          '</tr>';
        }).join('');
      }
      renderPagination(totalPages);
    }).catch(function () {
      tableBody.innerHTML = '<tr class="empty-row"><td colspan="6">加载失败</td></tr>';
    });
  }

  function renderPagination(totalPages) {
    pageInfo.textContent = '共 ' + totalRecords + ' 条记录，第 ' + currentPage + ' / ' + totalPages + ' 页';

    var h = '';
    h += '<button ' + (currentPage <= 1 ? 'disabled' : '') + ' data-page="' + (currentPage - 1) + '">上一页</button>';

    var maxVisible = 6;
    var sp = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    var ep = Math.min(totalPages, sp + maxVisible - 1);
    if (ep - sp < maxVisible - 1) sp = Math.max(1, ep - maxVisible + 1);

    if (sp > 1) { h += '<button data-page="1">1</button>'; if (sp > 2) h += '<button disabled>...</button>'; }
    for (var p = sp; p <= ep; p++) {
      h += '<button class="' + (p === currentPage ? 'active' : '') + '" data-page="' + p + '">' + p + '</button>';
    }
    if (ep < totalPages) { if (ep < totalPages - 1) h += '<button disabled>...</button>'; h += '<button data-page="' + totalPages + '">' + totalPages + '</button>'; }
    h += '<button ' + (currentPage >= totalPages ? 'disabled' : '') + ' data-page="' + (currentPage + 1) + '">下一页</button>';
    paginationCtls.innerHTML = h;
  }

  // ─── Event delegation ───────────────────────────────────────
  paginationCtls.addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-page]');
    if (!btn || btn.disabled) return;
    currentPage = parseInt(btn.getAttribute('data-page'));
    renderTable();
  });

  tableBody.addEventListener('click', function (e) {
    var editBtn = e.target.closest('[data-edit]');
    var delBtn  = e.target.closest('[data-delete]');
    if (editBtn) openEditModal(parseInt(editBtn.getAttribute('data-edit')));
    if (delBtn)  openDeleteConfirm(parseInt(delBtn.getAttribute('data-delete')));
  });

  searchInput.addEventListener('input', function () {
    searchKeyword = this.value;
    currentPage = 1;
    renderTable();
  });

  pageSizeSelect.addEventListener('change', function () {
    pageSize = parseInt(this.value);
    currentPage = 1;
    renderTable();
  });

  // ─── Modals ─────────────────────────────────────────────────
  // Add
  $('#btnAdd').addEventListener('click', openAddModal);
  $('#btnFormClose').addEventListener('click', closeFormModal);
  $('#btnFormCancel').addEventListener('click', closeFormModal);
  $('#formSubmitBtn').addEventListener('click', submitForm);
  $('#formModalOverlay').addEventListener('click', function (e) { if (e.target === this) closeFormModal(); });

  // Delete
  $('#btnDeleteClose').addEventListener('click', closeDeleteModal);
  $('#btnDeleteCancel').addEventListener('click', closeDeleteModal);
  $('#btnDeleteConfirm').addEventListener('click', confirmDelete);
  $('#deleteModalOverlay').addEventListener('click', function (e) { if (e.target === this) closeDeleteModal(); });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { closeFormModal(); closeDeleteModal(); }
  });

  function clearFormErrors() {
    ['#errorUsername','#errorPhone','#errorEmail'].forEach(function (s) { $(s).classList.remove('visible'); });
    ['#inputUsername','#inputPhone','#inputEmail'].forEach(function (s) { $(s).classList.remove('error'); });
  }

  function openAddModal() {
    editingUserId = null;
    $('#formModalTitle').textContent = '新增用户';
    $('#formSubmitBtn').textContent = '确认添加';
    $('#inputUsername').value = '';
    $('#inputPhone').value = '';
    $('#inputEmail').value = '';
    clearFormErrors();
    $('#formModalOverlay').classList.add('active');
    $('#inputUsername').focus();
  }

  function openEditModal(id) {
    // Fetch from current page data or API
    fetch(API_BASE + '/' + id)
      .then(function (r) { return r.json(); })
      .then(function (json) {
        if (json.code === 200 && json.data) {
          fillEditForm(json.data);
        }
      })
      .catch(function () {
        // Mock fallback
        for (var i = 0; i < mockUsers.length; i++) {
          if (mockUsers[i].id === id) { fillEditForm(mockUsers[i]); return; }
        }
      });
  }

  function fillEditForm(user) {
    editingUserId = user.id;
    $('#formModalTitle').textContent = '编辑用户';
    $('#formSubmitBtn').textContent = '确认更新';
    $('#inputUsername').value = user.username || '';
    $('#inputPhone').value = user.phone || '';
    $('#inputEmail').value = user.email || '';
    clearFormErrors();
    $('#formModalOverlay').classList.add('active');
  }

  function closeFormModal() {
    $('#formModalOverlay').classList.remove('active');
    editingUserId = null;
  }

  function validateForm(data) {
    var valid = true;
    clearFormErrors();

    if (!data.username.trim()) {
      $('#errorUsername').textContent = '用户名不能为空';
      $('#errorUsername').classList.add('visible');
      $('#inputUsername').classList.add('error');
      valid = false;
    }

    var phoneRe = /^1[3-9]\d{9}$/;
    if (!data.phone.trim()) {
      $('#errorPhone').textContent = '手机号不能为空';
      $('#errorPhone').classList.add('visible');
      $('#inputPhone').classList.add('error');
      valid = false;
    } else if (!phoneRe.test(data.phone.trim())) {
      $('#errorPhone').textContent = '手机号格式不正确（11位，1开头）';
      $('#errorPhone').classList.add('visible');
      $('#inputPhone').classList.add('error');
      valid = false;
    }

    if (data.email.trim()) {
      var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRe.test(data.email.trim())) {
        $('#errorEmail').textContent = '邮箱格式不正确';
        $('#errorEmail').classList.add('visible');
        $('#inputEmail').classList.add('error');
        valid = false;
      }
    }
    return valid;
  }

  function submitForm() {
    var data = {
      username: $('#inputUsername').value,
      phone: $('#inputPhone').value,
      email: $('#inputEmail').value
    };
    if (!validateForm(data)) return;

    var done = function () {
      showToast(editingUserId !== null ? '用户更新成功' : '用户添加成功', 'success');
      closeFormModal();
      renderTable();
    };
    var fail = function (msg) { showToast(msg || '操作失败', 'error'); };

    if (editingUserId !== null) {
      updateUser(editingUserId, data, done, fail);
    } else {
      addUser(data, done, fail);
    }
  }

  // Delete confirm
  function openDeleteConfirm(id) {
    deleteTargetId = id;
    // Try API first for name, fall back
    fetch(API_BASE + '/' + id)
      .then(function (r) { return r.json(); })
      .then(function (json) {
        if (json.code === 200 && json.data) {
          $('#deleteConfirmText').textContent =
            '确定要删除用户\u300c' + json.data.username + '\u300d(ID: ' + json.data.id + ') 吗？此操作不可撤销。';
        }
      })
      .catch(function () {
        for (var i = 0; i < mockUsers.length; i++) {
          if (mockUsers[i].id === id) {
            $('#deleteConfirmText').textContent =
              '确定要删除用户\u300c' + mockUsers[i].username + '\u300d(ID: ' + id + ') 吗？此操作不可撤销。';
            return;
          }
        }
        $('#deleteConfirmText').textContent = '确定要删除此用户吗？此操作不可撤销。';
      });
    $('#deleteModalOverlay').classList.add('active');
  }

  function closeDeleteModal() {
    $('#deleteModalOverlay').classList.remove('active');
    deleteTargetId = null;
  }

  function confirmDelete() {
    if (deleteTargetId === null) return;
    deleteUser(deleteTargetId, function () {
      showToast('用户删除成功', 'success');
      closeDeleteModal();
      renderTable();
    }, function (msg) {
      showToast(msg || '删除失败', 'error');
    });
  }

  // ─── Toast ──────────────────────────────────────────────────
  function showToast(msg, type) {
    var old = document.querySelector('.toast');
    if (old) old.parentNode.removeChild(old);
    var d = document.createElement('div');
    d.className = 'toast toast-' + type;
    d.textContent = msg;
    document.body.appendChild(d);
    setTimeout(function () { d.parentNode.removeChild(d); }, 2000);
  }

  // ─── Init: detect API ───────────────────────────────────────
  function init() {
    mockUsers = createSeedUsers();
    nextMockId = mockUsers.length + 1;
    totalRecords = mockUsers.length;

    // Try to reach the backend
    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, API_TIMEOUT);

    fetch(API_BASE + '?page=1&size=1', { signal: controller.signal })
      .then(function (r) { return r.json(); })
      .then(function (json) {
        clearTimeout(timer);
        if (json.code === 200) {
          useApi = true;
          totalRecords = (json.data && json.data.total) || 0;
          setModeUI('live');
        } else {
          useApi = false;
          setModeUI('mock');
        }
        renderTable();
      })
      .catch(function () {
        clearTimeout(timer);
        useApi = false;
        setModeUI('mock');
        renderTable();
      });
  }

  function setModeUI(mode) {
    if (mode === 'live') {
      modeBadge.textContent = 'API';
      modeBadge.className = 'mode-badge live';
    } else {
      modeBadge.textContent = 'Mock';
      modeBadge.className = 'mode-badge mock';
    }
  }

  // Start
  init();

})();
