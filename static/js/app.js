// NexusMarket State Management - Razorpay INR Edition
let currentUser = null;
let accessToken = localStorage.getItem('access_token') || null;
let refreshToken = localStorage.getItem('refresh_token') || null;
let cart = JSON.parse(localStorage.getItem('cart') || '[]');
let wishlist = new Set(JSON.parse(localStorage.getItem('wishlist') || '[]'));
let categories = [];
let products = [];
let currentCategory = null;
let appliedCoupon = null;

// Currency Formatter for Indian Rupees (₹)
function formatRupees(amount) {
    return '₹' + Number(amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Initialize App on DOM Load
document.addEventListener('DOMContentLoaded', async () => {
    updateCartBadge();
    updateWishlistBadge();
    await loadCategories();
    await loadProducts();
    if (accessToken) {
        await fetchUserProfile();
    }
});

// Toast System
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? 'bi-check-circle-fill' : (type === 'error' ? 'bi-exclamation-triangle-fill' : 'bi-info-circle-fill');
    toast.innerHTML = `<i class="bi ${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// API Helper with Token Auto-Refresh
async function apiFetch(url, options = {}) {
    options.headers = options.headers || {};
    if (accessToken) {
        options.headers['Authorization'] = `Bearer ${accessToken}`;
    }
    if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
    }

    let response = await fetch(url, options);

    if (response.status === 401 && refreshToken && !url.includes('/auth/refresh')) {
        const refreshed = await attemptTokenRefresh();
        if (refreshed) {
            options.headers['Authorization'] = `Bearer ${accessToken}`;
            response = await fetch(url, options);
        } else {
            logout();
        }
    }

    return response;
}

async function attemptTokenRefresh() {
    try {
        const res = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken })
        });
        if (res.ok) {
            const data = await res.json();
            accessToken = data.access_token;
            localStorage.setItem('access_token', accessToken);
            return true;
        }
    } catch (e) { console.error('Refresh token failed:', e); }
    return false;
}

// User Profile & Authentication
async function fetchUserProfile() {
    try {
        const res = await apiFetch('/api/auth/me');
        if (res.ok) {
            currentUser = await res.json();
            renderUserMenu();
        } else {
            logout();
        }
    } catch (e) {
        console.error('Failed to fetch profile:', e);
    }
}

function renderUserMenu() {
    const userMenu = document.getElementById('userMenu');
    const vendorNavBtn = document.getElementById('vendorNavBtn');
    const adminNavBtn = document.getElementById('adminNavBtn');

    if (!currentUser) {
        userMenu.innerHTML = `
            <button class="btn btn-primary btn-sm" onclick="openAuthModal('login')">
                <i class="bi bi-box-arrow-in-right"></i> Login / Register
            </button>
        `;
        vendorNavBtn.style.display = 'none';
        adminNavBtn.style.display = 'none';
        return;
    }

    vendorNavBtn.style.display = currentUser.role === 'vendor' ? 'flex' : 'none';
    adminNavBtn.style.display = currentUser.role === 'admin' ? 'flex' : 'none';

    userMenu.innerHTML = `
        <div class="flex-between gap-2">
            <span class="text-sm font-semibold text-primary"><i class="bi bi-person-circle"></i> ${currentUser.full_name} (${currentUser.role})</span>
            <button class="btn btn-sm btn-outline" onclick="logout()"><i class="bi bi-box-arrow-right"></i></button>
        </div>
    `;
}

async function quickLogin(email, password) {
    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
            accessToken = data.access_token;
            refreshToken = data.refresh_token;
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('refresh_token', refreshToken);
            await fetchUserProfile();
            showToast(`Logged in as ${currentUser.full_name}`, 'success');

            if (currentUser.role === 'vendor') switchView('vendor-dashboard');
            else if (currentUser.role === 'admin') switchView('admin-dashboard');
            else switchView('shop');
        } else {
            showToast(data.detail || 'Login failed', 'error');
        }
    } catch (e) {
        showToast('Login request error', 'error');
    }
}

async function logout() {
    if (accessToken) {
        apiFetch('/api/auth/logout', { method: 'POST' });
    }
    currentUser = null;
    accessToken = null;
    refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    renderUserMenu();
    switchView('shop');
    showToast('Logged out successfully', 'info');
}

// Navigation & View Switching
function switchView(viewName) {
    document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));

    if (viewName === 'shop') {
        document.getElementById('shopView').classList.add('active');
        loadProducts();
    } else if (viewName === 'orders') {
        document.getElementById('ordersView').classList.add('active');
        loadCustomerOrders();
    } else if (viewName === 'vendor-dashboard') {
        if (!currentUser || currentUser.role !== 'vendor') {
            showToast('Vendor access required', 'error');
            return;
        }
        document.getElementById('vendorView').classList.add('active');
        loadVendorDashboard();
    } else if (viewName === 'admin-dashboard') {
        if (!currentUser || currentUser.role !== 'admin') {
            showToast('Admin access required', 'error');
            return;
        }
        document.getElementById('adminView').classList.add('active');
        loadAdminDashboard();
    }
}

// Catalog Loading & Filtering
async function loadCategories() {
    try {
        const res = await fetch('/api/products/categories');
        if (res.ok) {
            categories = await res.json();
            renderCategories();
        }
    } catch (e) { console.error('Load categories failed:', e); }
}

function renderCategories() {
    const container = document.getElementById('categoryPills');
    let html = `<div class="cat-pill ${currentCategory === null ? 'active' : ''}" onclick="selectCategory(null)"><i class="bi bi-grid"></i> All Items</div>`;
    categories.forEach(c => {
        html += `
            <div class="cat-pill ${currentCategory === c.id ? 'active' : ''}" onclick="selectCategory(${c.id})">
                <i class="bi ${c.icon}"></i> ${c.name}
            </div>
        `;
    });
    container.innerHTML = html;
}

function selectCategory(catId) {
    currentCategory = catId;
    renderCategories();
    filterProducts();
}

async function loadProducts() {
    try {
        const res = await fetch('/api/products/');
        if (res.ok) {
            products = await res.json();
            document.getElementById('heroProductCount').innerText = `${products.length}+`;
            filterProducts();
        }
    } catch (e) { console.error('Load products failed:', e); }
}

function filterProducts() {
    const searchVal = document.getElementById('searchInput').value.toLowerCase().trim();
    const priceVal = document.getElementById('priceFilter').value;

    let filtered = products.filter(p => {
        const matchesSearch = !searchVal || p.name.toLowerCase().includes(searchVal) || (p.description && p.description.toLowerCase().includes(searchVal)) || (p.vendor_store_name && p.vendor_store_name.toLowerCase().includes(searchVal));
        const matchesCategory = currentCategory === null || p.category_id === currentCategory;
        
        let matchesPrice = true;
        if (priceVal === '0-5000') matchesPrice = p.price <= 5000;
        else if (priceVal === '5000-10000') matchesPrice = p.price > 5000 && p.price <= 10000;
        else if (priceVal === '10000-50000') matchesPrice = p.price > 10000;

        return matchesSearch && matchesCategory && matchesPrice;
    });

    renderProductsGrid(filtered);
}

function handleSearch(e) {
    if (e.key === 'Enter') triggerSearch();
    else filterProducts();
}

function triggerSearch() {
    filterProducts();
}

function renderProductsGrid(items) {
    const grid = document.getElementById('productsGrid');
    document.getElementById('catalogResultCount').innerText = `Showing ${items.length} items`;

    if (items.length === 0) {
        grid.innerHTML = `<div class="card glass p-4 text-center w-100"><i class="bi bi-inbox text-muted text-2xl"></i><p class="mt-2 text-muted">No products found matching criteria.</p></div>`;
        return;
    }

    let html = '';
    items.forEach(p => {
        const isWish = wishlist.has(p.id);
        const stars = '★'.repeat(Math.round(p.rating_avg)) + '☆'.repeat(5 - Math.round(p.rating_avg));
        html += `
            <div class="product-card">
                <div class="product-img-wrapper">
                    <img src="${p.image_url}" alt="${p.name}" loading="lazy">
                    <button class="wishlist-btn ${isWish ? 'active' : ''}" onclick="toggleWishlist(${p.id})">
                        <i class="bi ${isWish ? 'bi-heart-fill' : 'bi-heart'}"></i>
                    </button>
                    <span class="vendor-badge"><i class="bi bi-shop"></i> ${p.vendor_store_name}</span>
                </div>
                <div class="product-body">
                    <span class="product-cat">${p.category_name}</span>
                    <h3 class="product-title" onclick="openProductDetailModal(${p.id})">${p.name}</h3>
                    <div class="product-rating">${stars} <span>(${p.rating_count})</span></div>
                    <div class="product-footer">
                        <span class="product-price">${formatRupees(p.price)}</span>
                        <button class="btn btn-sm btn-primary" onclick="addToCart(${p.id})">
                            <i class="bi bi-cart-plus"></i> Add
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    grid.innerHTML = html;
}

// Product Details & Reviews Modal
async function openProductDetailModal(productId) {
    try {
        const pRes = await fetch(`/api/products/${productId}`);
        const rRes = await fetch(`/api/reviews/product/${productId}`);
        if (pRes.ok) {
            const p = await pRes.json();
            const reviews = rRes.ok ? await rRes.json() : [];
            const container = document.getElementById('productDetailContent');

            let reviewsHtml = '';
            reviews.forEach(r => {
                reviewsHtml += `
                    <div class="review-item border-bottom py-2">
                        <div class="flex-between">
                            <strong>${r.customer_name}</strong>
                            <span class="text-amber">★ ${r.rating}/5</span>
                        </div>
                        <p class="text-sm text-muted mt-1">${r.comment || 'No comment provided.'}</p>
                    </div>
                `;
            });

            container.innerHTML = `
                <div class="product-img-large">
                    <img src="${p.image_url}" alt="${p.name}" style="width:100%; border-radius:12px; height:280px; object-fit:cover;">
                </div>
                <div class="product-info-details">
                    <span class="text-primary font-semibold">${p.category_name} | ${p.vendor_store_name}</span>
                    <h2 class="mt-1">${p.name}</h2>
                    <h3 class="text-emerald my-2">${formatRupees(p.price)} <span class="text-sm text-muted font-normal">(${p.stock} in stock)</span></h3>
                    <p class="text-muted text-sm mb-3">${p.description}</p>
                    <button class="btn btn-emerald btn-block" onclick="addToCart(${p.id}); closeModal('productModal');">
                        <i class="bi bi-cart-plus"></i> Add to Cart
                    </button>
                </div>
                <div class="product-reviews-section mt-4" style="grid-column: 1 / -1;">
                    <h4><i class="bi bi-star"></i> Customer Reviews (${reviews.length})</h4>
                    <div class="reviews-list my-3">${reviewsHtml || '<p class="text-muted text-sm">No reviews yet for this product.</p>'}</div>
                    ${currentUser ? `
                        <form onsubmit="handleReviewSubmit(event, ${p.id})" class="mt-3 card p-3 glass">
                            <h5>Write a Verified Review</h5>
                            <div class="form-row mt-2">
                                <div class="col">
                                    <select id="revRating" class="form-select">
                                        <option value="5">5 Stars - Excellent</option>
                                        <option value="4">4 Stars - Very Good</option>
                                        <option value="3">3 Stars - Average</option>
                                    </select>
                                </div>
                                <div class="col-8">
                                    <input type="text" id="revComment" required placeholder="Share your experience..." class="form-input">
                                </div>
                            </div>
                            <button type="submit" class="btn btn-sm btn-primary mt-2">Submit Review</button>
                        </form>
                    ` : '<p class="text-sm text-muted">Please log in to submit a review.</p>'}
                </div>
            `;
            openModal('productModal');
        }
    } catch (e) { showToast('Error loading product details', 'error'); }
}

async function handleReviewSubmit(e, productId) {
    e.preventDefault();
    const rating = parseInt(document.getElementById('revRating').value);
    const comment = document.getElementById('revComment').value;

    const res = await apiFetch('/api/reviews/', {
        method: 'POST',
        body: { product_id: productId, rating, comment }
    });

    if (res.ok) {
        showToast('Review submitted successfully!', 'success');
        openProductDetailModal(productId);
    } else {
        showToast('Failed to submit review', 'error');
    }
}

// Wishlist
async function toggleWishlist(productId) {
    if (!currentUser) {
        showToast('Please login to save products to wishlist', 'info');
        openAuthModal('login');
        return;
    }

    if (wishlist.has(productId)) {
        wishlist.delete(productId);
        await apiFetch(`/api/wishlist/${productId}`, { method: 'DELETE' });
        showToast('Removed from Wishlist', 'info');
    } else {
        wishlist.add(productId);
        await apiFetch('/api/wishlist/', {
            method: 'POST',
            body: { product_id: productId }
        });
        showToast('Saved to Wishlist!', 'success');
    }
    localStorage.setItem('wishlist', JSON.stringify(Array.from(wishlist)));
    updateWishlistBadge();
    filterProducts();
}

function updateWishlistBadge() {
    document.getElementById('wishlistBadge').innerText = wishlist.size;
}

async function openWishlistModal() {
    if (!currentUser) {
        openAuthModal('login');
        return;
    }
    const container = document.getElementById('wishlistItemsList');
    container.innerHTML = '<p class="text-muted">Loading wishlist...</p>';
    openModal('wishlistModal');

    const res = await apiFetch('/api/wishlist/');
    if (res.ok) {
        const items = await res.json();
        if (items.length === 0) {
            container.innerHTML = '<p class="text-muted text-center py-3">Your wishlist is empty.</p>';
            return;
        }

        let html = '';
        items.forEach(w => {
            if (w.product) {
                html += `
                    <div class="cart-item-card align-center">
                        <img src="${w.product.image_url}" class="cart-item-img">
                        <div class="flex-1">
                            <h4 class="text-sm">${w.product.name}</h4>
                            <strong class="text-emerald">${formatRupees(w.product.price)}</strong>
                        </div>
                        <button class="btn btn-sm btn-primary" onclick="addToCart(${w.product.id})">Add to Cart</button>
                        <button class="btn-icon" onclick="toggleWishlist(${w.product.id}); openWishlistModal();"><i class="bi bi-trash"></i></button>
                    </div>
                `;
            }
        });
        container.innerHTML = html;
    }
}

// Shopping Cart & Checkout
function addToCart(productId) {
    const prod = products.find(p => p.id === productId);
    if (!prod) return;

    const existing = cart.find(item => item.product_id === productId);
    if (existing) {
        if (existing.quantity < prod.stock) existing.quantity++;
        else { showToast(`Only ${prod.stock} items available in stock`, 'error'); return; }
    } else {
        cart.push({
            product_id: prod.id,
            name: prod.name,
            price: prod.price,
            image_url: prod.image_url,
            vendor_id: prod.vendor_id,
            vendor_store_name: prod.vendor_store_name,
            quantity: 1
        });
    }

    saveCart();
    showToast(`Added '${prod.name}' to cart!`, 'success');
}

function updateCartQuantity(productId, delta) {
    const item = cart.find(i => i.product_id === productId);
    if (!item) return;
    item.quantity += delta;
    if (item.quantity <= 0) {
        cart = cart.filter(i => i.product_id !== productId);
    }
    saveCart();
    renderCartDrawer();
}

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartBadge();
}

function updateCartBadge() {
    const totalQty = cart.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById('cartBadge').innerText = totalQty;
}

function openCartDrawer() {
    renderCartDrawer();
    document.getElementById('cartDrawer').classList.add('active');
}

function closeCartDrawer() {
    document.getElementById('cartDrawer').classList.remove('active');
}

function renderCartDrawer() {
    const container = document.getElementById('cartBody');
    if (cart.length === 0) {
        container.innerHTML = '<div class="text-center text-muted py-5"><i class="bi bi-cart-x text-2xl"></i><p class="mt-2">Your cart is empty.</p></div>';
        updateCartTotals(0, 0);
        return;
    }

    let html = '';
    let subtotal = 0;

    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;

        html += `
            <div class="cart-item-card">
                <img src="${item.image_url}" class="cart-item-img">
                <div style="flex:1;">
                    <span class="text-xs text-primary font-semibold">${item.vendor_store_name}</span>
                    <h4 class="text-sm text-white">${item.name}</h4>
                    <span class="text-emerald text-sm font-bold">${formatRupees(item.price)}</span>
                    <div class="flex-between mt-2">
                        <div class="flex-between gap-2">
                            <button class="btn-icon" style="width:24px;height:24px;" onclick="updateCartQuantity(${item.product_id}, -1)">-</button>
                            <span class="text-sm font-semibold">${item.quantity}</span>
                            <button class="btn-icon" style="width:24px;height:24px;" onclick="updateCartQuantity(${item.product_id}, 1)">+</button>
                        </div>
                        <strong class="text-sm">${formatRupees(itemTotal)}</strong>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
    updateCartTotals(subtotal, appliedCoupon ? appliedCoupon.discount_amount : 0);
}

async function applyCoupon() {
    const code = document.getElementById('couponCodeInput').value.trim();
    if (!code) return;

    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const vendorIds = Array.from(new Set(cart.map(i => i.vendor_id)));

    try {
        const res = await fetch('/api/coupons/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code: code,
                cart_total: subtotal,
                vendor_ids: vendorIds
            })
        });

        const data = await res.json();
        if (res.ok && data.valid) {
            appliedCoupon = data;
            document.getElementById('couponAppliedMsg').innerText = `✓ ${data.message}`;
            document.getElementById('couponAppliedMsg').className = 'coupon-msg text-emerald text-sm font-semibold';
            renderCartDrawer();
            showToast(`Coupon '${data.code}' applied!`, 'success');
        } else {
            appliedCoupon = null;
            document.getElementById('couponAppliedMsg').innerText = `✗ ${data.detail || 'Invalid coupon'}`;
            document.getElementById('couponAppliedMsg').className = 'coupon-msg text-rose text-sm font-semibold';
            renderCartDrawer();
        }
    } catch (e) { showToast('Error validating coupon', 'error'); }
}

function updateCartTotals(subtotal, discount = 0) {
    const finalTotal = Math.max(0, subtotal - discount);
    document.getElementById('cartSubtotal').innerText = formatRupees(subtotal);
    document.getElementById('cartTotal').innerText = formatRupees(finalTotal);

    const discountLine = document.getElementById('discountLine');
    if (discount > 0) {
        discountLine.style.display = 'flex';
        document.getElementById('cartDiscount').innerText = `-${formatRupees(discount)}`;
    } else {
        discountLine.style.display = 'none';
    }
}

function openCheckoutModal() {
    if (!currentUser) {
        closeCartDrawer();
        openAuthModal('login');
        return;
    }
    if (cart.length === 0) {
        showToast('Your cart is empty', 'error');
        return;
    }

    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const discount = appliedCoupon ? appliedCoupon.discount_amount : 0;
    const finalTotal = Math.max(0, subtotal - discount);

    document.getElementById('checkoutFinalTotal').innerText = formatRupees(finalTotal);
    closeCartDrawer();
    openModal('checkoutModal');
}

async function handlePaymentSubmit(e) {
    e.preventDefault();
    const address = document.getElementById('checkoutAddress').value.trim();
    const paymentMethod = document.getElementById('paymentMethod').value;
    const payBtn = document.getElementById('payBtn');

    payBtn.disabled = true;
    payBtn.innerHTML = `<i class="bi bi-arrow-repeat spin"></i> Connecting to Razorpay Gateway...`;

    try {
        const payload = {
            items: cart.map(i => ({ product_id: i.product_id, quantity: i.quantity })),
            shipping_address: address,
            coupon_code: appliedCoupon ? appliedCoupon.code : null,
            payment_method: paymentMethod
        };

        const res = await apiFetch('/api/orders/checkout', {
            method: 'POST',
            body: payload
        });

        if (res.ok) {
            const order = await res.json();
            cart = [];
            appliedCoupon = null;
            saveCart();
            closeModal('checkoutModal');
            const paymentRef = order.items.length > 0 ? `pay_rzp_${Math.random().toString(36).substr(2, 9)}` : 'pay_rzp_success';
            showToast(`Razorpay Payment Successful! (${paymentRef}) Order #${order.id} confirmed.`, 'success');
            switchView('orders');
        } else {
            const err = await res.json();
            showToast(err.detail || 'Razorpay Payment failed', 'error');
        }
    } catch (e) {
        showToast('Razorpay payment processing error', 'error');
    } finally {
        payBtn.disabled = false;
        payBtn.innerHTML = `<i class="bi bi-lock-fill"></i> Pay Now via Razorpay (₹)`;
    }
}

// Order History
async function loadCustomerOrders() {
    if (!currentUser) return;
    const container = document.getElementById('ordersList');
    container.innerHTML = '<p class="text-muted">Loading order history...</p>';

    const res = await apiFetch('/api/orders/my-orders');
    if (res.ok) {
        const orders = await res.json();
        if (orders.length === 0) {
            container.innerHTML = '<div class="card glass p-4 text-center text-muted"><p>No previous orders found.</p></div>';
            return;
        }

        let html = '';
        orders.forEach(o => {
            let itemsHtml = '';
            o.items.forEach(item => {
                itemsHtml += `
                    <div class="flex-between py-2 border-bottom text-sm">
                        <span>${item.product_name} x ${item.quantity}</span>
                        <span class="badge ${item.item_status === 'DELIVERED' ? 'badge-accent' : ''}">${item.item_status}</span>
                        <strong>${formatRupees(item.price * item.quantity)}</strong>
                    </div>
                `;
            });

            html += `
                <div class="card glass p-4 mb-3">
                    <div class="flex-between border-bottom pb-2 mb-3">
                        <div>
                            <h4>Order #${o.id} <span class="badge badge-accent" style="font-size:0.7rem;">Razorpay Verified</span></h4>
                            <span class="text-xs text-muted">Placed on ${new Date(o.created_at).toLocaleDateString()}</span>
                        </div>
                        <div>
                            <span class="badge badge-accent">Payment: ${o.payment_status}</span>
                            <span class="badge">${o.order_status}</span>
                        </div>
                    </div>
                    <div class="order-items-list">${itemsHtml}</div>
                    <div class="flex-between mt-3 text-sm">
                        <span class="text-muted">Shipping to: ${o.shipping_address}</span>
                        <strong class="text-lg text-emerald">Total Paid: ${formatRupees(o.final_amount)}</strong>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    }
}

// Vendor Dashboard
async function loadVendorDashboard() {
    try {
        const vRes = await apiFetch('/api/vendors/me');
        if (!vRes.ok) return;
        const vendor = await vRes.json();

        document.getElementById('vendorStoreName').innerText = `${vendor.store_name} - Sales & Product Management`;
        document.getElementById('vendorTotalSales').innerText = formatRupees(vendor.total_sales);
        document.getElementById('vendorRating').innerText = `${vendor.rating.toFixed(1)} / 5.0`;

        // Load Products
        const pRes = await fetch(`/api/products/?vendor_id=${vendor.id}`);
        if (pRes.ok) {
            const vProducts = await pRes.json();
            document.getElementById('vendorProductCount').innerText = vProducts.length;

            const tbody = document.querySelector('#vendorProductsTable tbody');
            let html = '';
            vProducts.forEach(p => {
                html += `
                    <tr>
                        <td><strong>${p.name}</strong></td>
                        <td>${p.category_name}</td>
                        <td>${formatRupees(p.price)}</td>
                        <td>${p.stock}</td>
                        <td>★ ${p.rating_avg}</td>
                        <td><span class="badge badge-accent">${p.status}</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline" onclick="deleteVendorProduct(${p.id})"><i class="bi bi-trash"></i> Delete</button>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html || '<tr><td colspan="7" class="text-center text-muted">No products created yet.</td></tr>';
        }

        // Load Vendor Line Items Order Fulfillment
        const oRes = await apiFetch('/api/orders/vendor-orders');
        if (oRes.ok) {
            const vOrders = await oRes.json();
            const tbody = document.querySelector('#vendorOrdersTable tbody');
            let html = '';
            vOrders.forEach(item => {
                html += `
                    <tr>
                        <td>#${item.item_id}</td>
                        <td>Order #${item.order_id}</td>
                        <td>${item.product_name}</td>
                        <td>${item.quantity}</td>
                        <td>${formatRupees(item.total)}</td>
                        <td class="text-xs text-muted">${item.shipping_address}</td>
                        <td><span class="badge">${item.item_status}</span></td>
                        <td>
                            <select class="form-select form-select-sm" onchange="updateVendorOrderStatus(${item.item_id}, this.value)">
                                <option value="PROCESSING" ${item.item_status === 'PROCESSING' ? 'selected' : ''}>PROCESSING</option>
                                <option value="SHIPPED" ${item.item_status === 'SHIPPED' ? 'selected' : ''}>SHIPPED</option>
                                <option value="DELIVERED" ${item.item_status === 'DELIVERED' ? 'selected' : ''}>DELIVERED</option>
                            </select>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html || '<tr><td colspan="8" class="text-center text-muted">No line item orders to fulfill.</td></tr>';
        }
    } catch (e) { showToast('Error loading vendor dashboard', 'error'); }
}

async function deleteVendorProduct(productId) {
    if (!confirm('Are you sure you want to remove this product?')) return;
    const res = await apiFetch(`/api/products/${productId}`, { method: 'DELETE' });
    if (res.ok) {
        showToast('Product deleted', 'info');
        loadVendorDashboard();
    }
}

async function updateVendorOrderStatus(itemId, status) {
    const res = await apiFetch(`/api/orders/vendor-order-items/${itemId}/status`, {
        method: 'PUT',
        body: { order_status: status }
    });
    if (res.ok) {
        showToast(`Item status updated to ${status}`, 'success');
        loadVendorDashboard();
    }
}

function openAddProductModal() {
    const select = document.getElementById('prodCategory');
    let html = '';
    categories.forEach(c => html += `<option value="${c.id}">${c.name}</option>`);
    select.innerHTML = html;
    openModal('addProductModal');
}

async function handleAddProductSubmit(e) {
    e.preventDefault();
    const payload = {
        name: document.getElementById('prodName').value,
        category_id: parseInt(document.getElementById('prodCategory').value),
        price: parseFloat(document.getElementById('prodPrice').value),
        stock: parseInt(document.getElementById('prodStock').value),
        image_url: document.getElementById('prodImage').value || undefined,
        description: document.getElementById('prodDesc').value
    };

    const res = await apiFetch('/api/products/', {
        method: 'POST',
        body: payload
    });

    if (res.ok) {
        showToast('Product created successfully!', 'success');
        closeModal('addProductModal');
        loadVendorDashboard();
    } else {
        showToast('Failed to create product', 'error');
    }
}

// Admin Panel
async function loadAdminDashboard() {
    try {
        const statsRes = await apiFetch('/api/admin/stats');
        if (statsRes.ok) {
            const stats = await statsRes.json();
            document.getElementById('adminGMV').innerText = formatRupees(stats.total_gmv);
            document.getElementById('adminCommission').innerText = formatRupees(stats.platform_commission);
            document.getElementById('adminVendorCount').innerText = stats.total_vendors;
            document.getElementById('adminOrderCount').innerText = stats.total_orders;
        }

        // Vendors Moderation
        const vRes = await apiFetch('/api/admin/vendors');
        if (vRes.ok) {
            const vendors = await vRes.json();
            const tbody = document.querySelector('#adminVendorsTable tbody');
            let html = '';
            vendors.forEach(v => {
                html += `
                    <tr>
                        <td>#${v.id}</td>
                        <td><strong>${v.store_name}</strong></td>
                        <td>${v.owner_email}</td>
                        <td>${v.product_count}</td>
                        <td>${formatRupees(v.total_sales)}</td>
                        <td><span class="badge ${v.status === 'approved' ? 'badge-accent' : ''}">${v.status}</span></td>
                        <td>
                            ${v.status === 'approved' ? `
                                <button class="btn btn-sm btn-outline" onclick="setVendorStatus(${v.id}, 'suspended')">Suspend</button>
                            ` : `
                                <button class="btn btn-sm btn-emerald" onclick="setVendorStatus(${v.id}, 'approved')">Approve</button>
                            `}
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        }

        // Coupons
        const cRes = await fetch('/api/coupons/');
        if (cRes.ok) {
            const coupons = await cRes.json();
            const tbody = document.querySelector('#adminCouponsTable tbody');
            let html = '';
            coupons.forEach(c => {
                html += `
                    <tr>
                        <td><strong>${c.code}</strong></td>
                        <td>${c.discount_type}</td>
                        <td>${c.discount_type === 'percent' ? `${c.discount_value}%` : formatRupees(c.discount_value)}</td>
                        <td>${formatRupees(c.min_order_amount)}</td>
                        <td>${c.current_uses} / ${c.max_uses}</td>
                        <td>${c.vendor_id ? `Vendor #${c.vendor_id}` : 'Global Platform'}</td>
                        <td><span class="badge badge-accent">${c.is_active ? 'Active' : 'Inactive'}</span></td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        }
    } catch (e) { showToast('Error loading admin dashboard', 'error'); }
}

async function setVendorStatus(vendorId, status) {
    const res = await apiFetch(`/api/admin/vendors/${vendorId}/status?status=${status}`, { method: 'PUT' });
    if (res.ok) {
        showToast(`Vendor status set to ${status}`, 'success');
        loadAdminDashboard();
    }
}

function openCreateCouponModal() { openModal('createCouponModal'); }

async function handleCreateCouponSubmit(e) {
    e.preventDefault();
    const payload = {
        code: document.getElementById('coupCode').value,
        discount_type: document.getElementById('coupType').value,
        discount_value: parseFloat(document.getElementById('coupValue').value),
        min_order_amount: parseFloat(document.getElementById('coupMin').value),
        max_uses: parseInt(document.getElementById('coupMax').value)
    };

    const res = await apiFetch('/api/coupons/', {
        method: 'POST',
        body: payload
    });

    if (res.ok) {
        showToast('Coupon created!', 'success');
        closeModal('createCouponModal');
        loadAdminDashboard();
    } else {
        showToast('Failed to create coupon', 'error');
    }
}

// Modal Helpers
function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

function openAuthModal(tab = 'login') {
    switchAuthTab(tab);
    openModal('authModal');
}

function switchAuthTab(tab) {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));

    if (tab === 'login') {
        document.getElementById('tabLogin').classList.add('active');
        document.getElementById('loginForm').classList.add('active');
    } else if (tab === 'register') {
        document.getElementById('tabRegister').classList.add('active');
        document.getElementById('registerForm').classList.add('active');
    } else if (tab === 'forgot') {
        document.getElementById('tabForgot').classList.add('active');
        document.getElementById('forgotForm').classList.add('active');
    }
}

function toggleStoreNameInput() {
    const role = document.getElementById('regRole').value;
    document.getElementById('storeNameGroup').style.display = role === 'vendor' ? 'block' : 'none';
}

async function handleLoginSubmit(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    await quickLogin(email, password);
    closeModal('authModal');
}

async function handleRegisterSubmit(e) {
    e.preventDefault();
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const role = document.getElementById('regRole').value;
    const storeName = document.getElementById('regStoreName').value;

    const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: name, role, store_name: storeName })
    });

    if (res.ok) {
        showToast('Registration successful! Please log in.', 'success');
        switchAuthTab('login');
    } else {
        const err = await res.json();
        showToast(err.detail || 'Registration failed', 'error');
    }
}

async function handleForgotSubmit(e) {
    e.preventDefault();
    const email = document.getElementById('forgotEmail').value;
    const res = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    });

    if (res.ok) {
        const data = await res.json();
        showToast(`Reset code generated: ${data.reset_token}`, 'success');
        alert(`Reset Token for ${email}: ${data.reset_token}`);
        switchAuthTab('login');
    } else {
        showToast('Email not found', 'error');
    }
}
