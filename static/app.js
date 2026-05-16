/* Garage Sale Inventory App */

const API_BASE = '';
let currentPhotoBlob = null;
let currentPhotoPreview = null;
let selectedItems = new Set();
let allItems = [];
let platforms = [];
let categories = [];

// ─── Init ───────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initCamera();
  initNavigation();
  initForms();
  initModals();
  loadCategories();
  loadInventory();
  loadPlatforms();
});

function showToast(msg, type = 'info') {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.className = 'toast show ' + type;
  setTimeout(() => toast.classList.remove('show'), 2500);
}

function setLoading(on) {
  document.getElementById('loading').style.display = on ? 'flex' : 'none';
}

async function api(path, opts = {}) {
  const url = API_BASE + path;
  const res = await fetch(url, opts);
  if (!res.ok) {
    const err = await res.text().catch(() => res.statusText);
    throw new Error(err);
  }
  return res.json();
}

// ─── Camera ─────────────────────────────────────────────────────────────

function initCamera() {
  const video = document.getElementById('camera-video');
  const canvas = document.getElementById('camera-canvas');
  const preview = document.getElementById('photo-preview');
  const overlay = document.getElementById('camera-overlay');
  const controls = document.getElementById('camera-controls');

  document.getElementById('btn-start-camera').addEventListener('click', async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
      video.srcObject = stream;
      video.style.display = 'block';
      overlay.style.display = 'none';
      controls.style.display = 'flex';
      document.getElementById('btn-snap').style.display = 'inline-block';
      document.getElementById('btn-retake').style.display = 'none';
    } catch (e) {
      // Fallback to file input
      document.getElementById('file-input').click();
    }
  });

  document.getElementById('btn-upload-file').addEventListener('click', () => {
    document.getElementById('file-input').click();
  });

  document.getElementById('file-input').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      showPhoto(ev.target.result);
      currentPhotoBlob = file;
    };
    reader.readAsDataURL(file);
  });

  document.getElementById('btn-snap').addEventListener('click', () => {
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
    showPhoto(dataUrl);
    // Stop stream
    const stream = video.srcObject;
    if (stream) stream.getTracks().forEach(t => t.stop());
    video.style.display = 'none';
    controls.style.display = 'none';
    // Convert dataURL to blob for upload
    fetch(dataUrl).then(r => r.blob()).then(b => { currentPhotoBlob = b; });
  });

  document.getElementById('btn-retake').addEventListener('click', () => {
    preview.style.display = 'none';
    document.getElementById('item-form').style.display = 'none';
    overlay.style.display = 'flex';
    currentPhotoBlob = null;
    currentPhotoPreview = null;
  });

  function showPhoto(url) {
    preview.src = url;
    preview.style.display = 'block';
    document.getElementById('item-form').style.display = 'block';
    controls.style.display = 'flex';
    document.getElementById('btn-snap').style.display = 'none';
    document.getElementById('btn-retake').style.display = 'inline-block';
    currentPhotoPreview = url;
    // Auto-scroll to form
    setTimeout(() => document.getElementById('item-form').scrollIntoView({ behavior: 'smooth' }), 100);
  }
}

// ─── Navigation ─────────────────────────────────────────────────────────

function initNavigation() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const sectionId = btn.dataset.section;
      document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
      document.getElementById(sectionId).classList.add('active');
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      if (sectionId === 'inventory-section') loadInventory();
    });
  });
}

// ─── Forms ──────────────────────────────────────────────────────────────

function initForms() {
  // Item form submit
  document.getElementById('item-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData();
    formData.append('name', document.getElementById('item-name').value);
    formData.append('brand', document.getElementById('item-brand').value);
    formData.append('description', document.getElementById('item-description').value);
    formData.append('category', document.getElementById('item-category').value);
    formData.append('condition', document.getElementById('item-condition').value);
    formData.append('price', document.getElementById('item-price').value || '0');
    const suggested = document.getElementById('suggested-price-value').textContent;
    if (suggested && suggested !== '0') formData.append('suggested_price', suggested);
    if (currentPhotoBlob) {
      formData.append('image', currentPhotoBlob, 'photo.jpg');
    }
    setLoading(true);
    try {
      const item = await api('/api/items', { method: 'POST', body: formData });
      showToast('Item saved!');
      resetForm();
      // If AI is available, auto-analyze
      if (item.image_path) {
        autoAnalyze(item.id);
      }
    } catch (err) {
      showToast('Error: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  });

  // Find comps
  document.getElementById('btn-find-comps').addEventListener('click', async () => {
    const name = document.getElementById('item-name').value;
    const brand = document.getElementById('item-brand').value;
    if (!name) { showToast('Enter item name first', 'error'); return; }
    // Create temp item for comps
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('name', name);
      formData.append('brand', brand);
      const item = await api('/api/items', { method: 'POST', body: formData });
      const comps = await api('/api/items/' + item.id + '/comps', { method: 'POST' });
      showCompsModal(comps, item.id);
    } catch (err) {
      showToast('Error: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  });

  document.getElementById('btn-use-suggested').addEventListener('click', () => {
    const val = document.getElementById('suggested-price-value').textContent;
    document.getElementById('item-price').value = val;
  });

  // Use comp price
  document.getElementById('btn-use-comp-price').addEventListener('click', () => {
    const val = document.getElementById('comps-results').dataset.suggestedPrice;
    if (val) {
      document.getElementById('item-price').value = val;
      document.getElementById('suggested-price-value').textContent = val;
      document.getElementById('suggested-price-display').style.display = 'block';
    }
    closeModal('comps-modal');
  });
}

function resetForm() {
  document.getElementById('item-form').reset();
  document.getElementById('photo-preview').style.display = 'none';
  document.getElementById('item-form').style.display = 'none';
  document.getElementById('camera-overlay').style.display = 'flex';
  document.getElementById('camera-controls').style.display = 'none';
  document.getElementById('suggested-price-display').style.display = 'none';
  document.getElementById('ai-status').textContent = '';
  currentPhotoBlob = null;
  currentPhotoPreview = null;
}

async function autoAnalyze(itemId) {
  try {
    document.getElementById('ai-status').textContent = '🤖 Analyzing photo...';
    const result = await api('/api/items/' + itemId + '/analyze', { method: 'POST' });
    document.getElementById('ai-status').textContent = '';
    if (result.analysis && result.analysis.name) {
      document.getElementById('item-name').value = result.analysis.name || '';
      document.getElementById('item-brand').value = result.analysis.brand || '';
      document.getElementById('item-description').value = result.analysis.description || '';
      if (result.analysis.category) document.getElementById('item-category').value = result.analysis.category;
      if (result.analysis.condition) document.getElementById('item-condition').value = result.analysis.condition;
      showToast('🎯 AI identified: ' + result.analysis.name);
    }
    if (result.analysis && result.analysis.message) {
      document.getElementById('ai-status').textContent = result.analysis.message;
    }
  } catch (e) {
    console.error('AI analyze error:', e);
  }
}

// ─── Inventory ──────────────────────────────────────────────────────────

async function loadCategories() {
  try {
    const data = await api('/api/categories');
    categories = data.categories || [];
    const select = document.getElementById('item-category');
    select.innerHTML = '<option value="Other">Other</option>';
    categories.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.name;
      opt.textContent = c.name;
      select.appendChild(opt);
    });
  } catch (e) { console.error(e); }
}

async function loadInventory() {
  try {
    const data = await api('/api/items?limit=1000');
    allItems = data.items || [];
    renderInventory(allItems);
    updateCounts();
  } catch (e) {
    showToast('Failed to load inventory', 'error');
  }
}

function renderInventory(items) {
  const grid = document.getElementById('inventory-grid');
  const empty = document.getElementById('empty-state');
  if (!items.length) {
    grid.innerHTML = '';
    empty.style.display = 'block';
    return;
  }
  empty.style.display = 'none';
  grid.innerHTML = items.map(item => `
    <div class="item-card" data-id="${item.id}" data-status="${item.status}">
      <div class="item-select">
        <input type="checkbox" class="item-checkbox" data-id="${item.id}">
      </div>
      <div class="item-thumb">
        ${item.image_path ? `<img src="${API_BASE}/uploads/${item.image_path.split('/').pop()}" alt="">` : '<span class="no-photo">📷</span>'}
      </div>
      <div class="item-info">
        <h4>${escapeHtml(item.name || 'Untitled')}</h4>
        <p class="item-brand">${escapeHtml(item.brand || '')}</p>
        <p class="item-category">${escapeHtml(item.category || '')} • ${item.condition || ''}</p>
        <div class="item-price-row">
          <span class="price">$${Number(item.price || 0).toFixed(2)}</span>
          ${item.suggested_price ? `<span class="suggested">sugg. $${Number(item.suggested_price).toFixed(2)}</span>` : ''}
        </div>
        <span class="status-badge status-${item.status || 'draft'}">${item.status || 'draft'}</span>
      </div>
      <div class="item-actions">
        <button class="btn btn-icon" onclick="editItem('${item.id}')" title="Edit">✏️</button>
        <button class="btn btn-icon" onclick="deleteItem('${item.id}')" title="Delete">🗑️</button>
        <button class="btn btn-icon" onclick="showListingsModal('${item.id}')" title="List">🚀</button>
      </div>
    </div>
  `).join('');

  // Checkbox handlers
  document.querySelectorAll('.item-checkbox').forEach(cb => {
    cb.addEventListener('change', (e) => {
      if (e.target.checked) selectedItems.add(e.target.dataset.id);
      else selectedItems.delete(e.target.dataset.id);
      updateBulkBar();
    });
  });

  // Filter handlers
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.dataset.filter;
      const filtered = filter === 'all' ? allItems : allItems.filter(i => (i.status || 'draft') === filter);
      renderInventory(filtered);
    });
  });
}

function updateCounts() {
  document.getElementById('inventory-count').textContent = allItems.length + ' item' + (allItems.length !== 1 ? 's' : '');
  document.getElementById('nav-badge').textContent = allItems.length;
}

function updateBulkBar() {
  const bar = document.getElementById('bulk-bar');
  bar.style.display = selectedItems.size > 0 ? 'flex' : 'none';
}

document.getElementById('select-all-checkbox').addEventListener('change', (e) => {
  const checkboxes = document.querySelectorAll('.item-checkbox');
  checkboxes.forEach(cb => {
    cb.checked = e.target.checked;
    if (e.target.checked) selectedItems.add(cb.dataset.id);
    else selectedItems.delete(cb.dataset.id);
  });
  updateBulkBar();
});

document.getElementById('btn-export-csv').addEventListener('click', () => {
  window.location.href = API_BASE + '/api/export/csv';
});

document.getElementById('btn-list-selected').addEventListener('click', () => {
  if (selectedItems.size === 0) { showToast('Select items first', 'error'); return; }
  showListingsModal(null, Array.from(selectedItems));
});

async function editItem(id) {
  const item = allItems.find(i => i.id === id);
  if (!item) return;
  document.getElementById('item-name').value = item.name || '';
  document.getElementById('item-brand').value = item.brand || '';
  document.getElementById('item-description').value = item.description || '';
  document.getElementById('item-category').value = item.category || 'Other';
  document.getElementById('item-condition').value = item.condition || 'Good';
  document.getElementById('item-price').value = item.price || '';
  if (item.suggested_price) {
    document.getElementById('suggested-price-value').textContent = item.suggested_price;
    document.getElementById('suggested-price-display').style.display = 'block';
  }
  document.getElementById('item-form').style.display = 'block';
  document.getElementById('camera-overlay').style.display = 'none';
  document.getElementById('camera-section').scrollIntoView({ behavior: 'smooth' });
  // Change save to update
  const form = document.getElementById('item-form');
  form.onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', document.getElementById('item-name').value);
    formData.append('brand', document.getElementById('item-brand').value);
    formData.append('description', document.getElementById('item-description').value);
    formData.append('category', document.getElementById('item-category').value);
    formData.append('condition', document.getElementById('item-condition').value);
    formData.append('price', document.getElementById('item-price').value || '0');
    setLoading(true);
    try {
      await api('/api/items/' + id, { method: 'PUT', body: formData });
      showToast('Item updated!');
      resetForm();
      loadInventory();
      form.onsubmit = null; // Reset to default
      initForms(); // Re-bind default submit
    } catch (err) {
      showToast('Error: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  };
}

async function deleteItem(id) {
  if (!confirm('Delete this item?')) return;
  try {
    await api('/api/items/' + id, { method: 'DELETE' });
    showToast('Deleted');
    loadInventory();
  } catch (e) {
    showToast('Error deleting', 'error');
  }
}

// ─── Platforms ──────────────────────────────────────────────────────────

async function loadPlatforms() {
  try {
    const data = await api('/api/platforms');
    platforms = data.platforms || [];
    renderPlatforms();
    renderPlatformCheckboxes();
  } catch (e) { console.error(e); }
}

function renderPlatforms() {
  const list = document.getElementById('platforms-list');
  list.innerHTML = platforms.map(p => `
    <div class="platform-card ${p.connected ? 'connected' : ''}">
      <div class="platform-icon">${platformIcon(p.platform)}</div>
      <div class="platform-info">
        <h4>${escapeHtml(p.name)}</h4>
        <span class="platform-status">${p.connected ? '✅ Connected' : '⚪ Not connected'}</span>
      </div>
      <button class="btn btn-sm ${p.connected ? 'btn-secondary' : 'btn-primary'}"
        onclick="showAuthModal('${p.platform}')">
        ${p.connected ? 'Reconnect' : 'Connect'}
      </button>
    </div>
  `).join('');
}

function platformIcon(platform) {
  const icons = {
    ebay: '📧', facebook_marketplace: '👥', craigslist: '📋',
    instagram: '📸', x: '💬', shopify: '🛍️',
    woocommerce: '📦', poshmark: '👗', mercari: '🏷️',
  };
  return icons[platform] || '🔗';
}

function renderPlatformCheckboxes() {
  const container = document.getElementById('platform-checkboxes');
  container.innerHTML = platforms.map(p => `
    <label class="platform-checkbox">
      <input type="checkbox" name="platform" value="${p.platform}">
      <span class="check-label">${platformIcon(p.platform)} ${escapeHtml(p.name)}</span>
    </label>
  `).join('');
}

function showAuthModal(platform) {
  const p = platforms.find(x => x.platform === platform);
  if (!p) return;
  document.getElementById('auth-modal-title').textContent = 'Connect ' + p.name;
  const form = document.getElementById('auth-form');
  form.innerHTML = '';
  if (!p.has_api) {
    form.innerHTML = `<p>This platform does not have an API. Listings will be generated as copy-paste text.</p>`;
  } else if (p.auth_type === 'api_key') {
    form.innerHTML = `
      <div class="form-group"><label>API Key</label><input type="text" id="auth-api-key" placeholder="Enter API key"></div>
      <div class="form-group"><label>Store URL</label><input type="text" id="auth-store-url" placeholder="https://your-store.myshopify.com"></div>
      <button type="button" class="btn btn-primary" id="btn-save-auth">Save</button>
    `;
  } else if (p.auth_type === 'oauth') {
    form.innerHTML = `<p>OAuth connection requires manual setup. Please visit the platform developer console to generate credentials, then paste them below.</p>`;
  } else if (p.auth_type === 'bearer') {
    form.innerHTML = `
      <div class="form-group"><label>Bearer Token</label><input type="text" id="auth-bearer" placeholder="Enter bearer token"></div>
      <button type="button" class="btn btn-primary" id="btn-save-auth">Save</button>
    `;
  }
  openModal('auth-modal');

  const saveBtn = document.getElementById('btn-save-auth');
  if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
      const creds = {};
      const keyInput = document.getElementById('auth-api-key');
      const urlInput = document.getElementById('auth-store-url');
      const bearerInput = document.getElementById('auth-bearer');
      if (keyInput) creds.api_key = keyInput.value;
      if (urlInput) creds.store_url = urlInput.value;
      if (bearerInput) creds.bearer_token = bearerInput.value;
      try {
        await api('/api/platforms/' + platform + '/connect', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: 'credentials=' + encodeURIComponent(JSON.stringify(creds)),
        });
        showToast(p.name + ' connected!');
        closeModal('auth-modal');
        loadPlatforms();
      } catch (e) {
        showToast('Connection failed', 'error');
      }
    });
  }
}

// ─── Listings ───────────────────────────────────────────────────────────

let currentListingItemIds = [];

function showListingsModal(singleId, batchIds = null) {
  currentListingItemIds = batchIds || (singleId ? [singleId] : []);
  document.getElementById('listings-preview').innerHTML = '';
  document.getElementById('btn-copy-all').style.display = 'none';
  openModal('listings-modal');
}

document.getElementById('btn-generate-listings').addEventListener('click', async () => {
  const checked = document.querySelectorAll('input[name="platform"]:checked');
  const selectedPlatforms = Array.from(checked).map(cb => cb.value);
  if (!selectedPlatforms.length) { showToast('Select at least one platform', 'error'); return; }
  if (!currentListingItemIds.length) { showToast('No items selected', 'error'); return; }

  setLoading(true);
  try {
    const data = await api('/api/batch/list', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'item_ids=' + encodeURIComponent(JSON.stringify(currentListingItemIds))
        + '&platforms=' + encodeURIComponent(JSON.stringify(selectedPlatforms)),
    });
    renderListingsPreview(data.batch, selectedPlatforms);
    document.getElementById('btn-copy-all').style.display = 'inline-block';
  } catch (e) {
    showToast('Error generating listings', 'error');
  } finally {
    setLoading(false);
  }
});

document.getElementById('btn-copy-all').addEventListener('click', () => {
  const text = document.getElementById('listings-preview').innerText;
  navigator.clipboard.writeText(text).then(() => showToast('Copied to clipboard!'));
});

function renderListingsPreview(batch, platforms) {
  const container = document.getElementById('listings-preview');
  container.innerHTML = batch.map(b => {
    const listings = platforms.map(p => {
      const listing = b.listings[p];
      if (!listing) return '';
      let content = '';
      if (p === 'instagram') {
        content = `<strong>Caption:</strong><br><pre>${escapeHtml(listing.caption || '')}</pre><br><strong>Hashtags:</strong> ${escapeHtml(listing.hashtags || '')}`;
      } else if (p === 'x') {
        content = `<pre>${escapeHtml(listing.text || '')}</pre>`;
      } else {
        content = `<strong>Title:</strong> ${escapeHtml(listing.title || listing.name || '')}<br><pre>${escapeHtml(listing.description || '')}</pre>`;
      }
      return `
        <div class="listing-block">
          <h5>${platformIcon(p)} ${escapeHtml(p)}</h5>
          ${content}
          <div class="listing-price">$${Number(listing.price || 0).toFixed(2)}</div>
          <button class="btn btn-sm btn-secondary" onclick="copyText(this)">📋 Copy</button>
        </div>
      `;
    }).join('');
    return `
      <div class="listing-item">
        <h4>${escapeHtml(b.item_name || 'Untitled')}</h4>
        ${listings}
      </div>
    `;
  }).join('');
}

function copyText(btn) {
  const block = btn.closest('.listing-block');
  const text = block.innerText.replace('📋 Copy', '').trim();
  navigator.clipboard.writeText(text).then(() => showToast('Copied!'));
}

// ─── Comps Modal ────────────────────────────────────────────────────────

function showCompsModal(comps, itemId) {
  const container = document.getElementById('comps-results');
  container.dataset.itemId = itemId;
  const suggestion = comps.suggestion || {};
  container.dataset.suggestedPrice = suggestion.suggested_price || '';

  let html = '';
  if (suggestion.suggested_price) {
    html += `<div class="comp-suggestion">
      <strong>💡 Suggested Price: $${Number(suggestion.suggested_price).toFixed(2)}</strong>
      <span>Range: $${Number(suggestion.range_low || 0).toFixed(2)} – $${Number(suggestion.range_high || 0).toFixed(2)}</span>
    </div>`;
  }
  html += '<div class="comp-results-list">';
  (comps.results || []).forEach(r => {
    html += `
      <div class="comp-result">
        <a href="${escapeHtml(r.url)}" target="_blank">${escapeHtml(r.title)}</a>
        ${r.extracted_price ? `<span class="comp-price">$${Number(r.extracted_price).toFixed(2)}</span>` : ''}
      </div>
    `;
  });
  html += '</div>';
  container.innerHTML = html;
  openModal('comps-modal');
}

// ─── Modals ─────────────────────────────────────────────────────────────

function initModals() {
  document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal(modal.id);
    });
  });
  document.getElementById('btn-close-comps').addEventListener('click', () => closeModal('comps-modal'));
  document.getElementById('btn-close-listings').addEventListener('click', () => closeModal('listings-modal'));
  document.getElementById('btn-close-auth').addEventListener('click', () => closeModal('auth-modal'));
}

function openModal(id) {
  document.getElementById(id).classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closeModal(id) {
  document.getElementById(id).classList.remove('show');
  document.body.style.overflow = '';
}

// ─── Utilities ──────────────────────────────────────────────────────────

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Service Worker for PWA
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').catch(() => {});
}
