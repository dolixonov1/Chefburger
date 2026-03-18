document.addEventListener('DOMContentLoaded', () => {
  // --- Data ---
  const menuItems = [
    { id: 1, name: "The Classic", desc: "Beef patty, cheddar, lettuce, tomato, special sauce", price: 32000, badge: "fire", badgeText: "Most Popular", cat: "popular", color: "#2d1a0a" },
    { id: 2, name: "Double Smash", desc: "Two smashed patties, American cheese, caramelized onions, pickles", price: 48000, badge: "fire", badgeText: "Most Popular", cat: "popular", color: "#1a0f06" },
    { id: 3, name: "Chef's Signature", desc: "Wagyu blend, truffle mayo, aged cheddar, arugula, red onion jam", price: 62000, badge: "chef", badgeText: "Chef's Choice", cat: "chef", color: "#0d1520" },
    { id: 4, name: "Spicy Inferno", desc: "Jalapeños, sriracha mayo, pepper jack, crispy bacon, ghost chilli sauce", price: 38000, badge: "new", badgeText: "New", cat: "popular", color: "#1a0805" },
    { id: 5, name: "Mushroom Melt", desc: "Sautéed mushrooms, swiss cheese, garlic aioli, brioche bun", price: 36000, badge: "chef", badgeText: "Chef's Choice", cat: "chef", color: "#0d1a0a" },
    { id: 6, name: "Crispy Fries", desc: "House-seasoned, double fried, served with dipping sauce", price: 14000, badge: null, badgeText: null, cat: "sides", color: "#1a1206" },
    { id: 7, name: "Onion Rings", desc: "Beer-battered, golden and crispy, with ranch dip", price: 16000, badge: null, badgeText: null, cat: "sides", color: "#1a0f06" },
    { id: 8, name: "The BBQ Stack", desc: "Beef patty, pulled pork, BBQ sauce, crispy onions, smoked cheddar", price: 52000, badge: "chef", badgeText: "Chef's Choice", cat: "chef", color: "#1a0905" }
  ];

  const reviews = [
    { name: "Alisher T.", loc: "Tashkent", text: "Honestly the best burger I've had anywhere. The smash patty is unreal...", initials: "AT" },
    { name: "Zulfiya M.", loc: "Tashkent", text: "Ordered for delivery and it arrived in 25 minutes, still hot...", initials: "ZM" },
    { name: "Bobur K.", loc: "Yunusabad", text: "Chef's Signature is next level. You can taste the quality of the meat...", initials: "BK" },
    { name: "Dilnoza R.", loc: "Chilanzar", text: "Vegetarian options are limited but the service is so friendly...", initials: "DR" },
    { name: "Jahongir A.", loc: "Tashkent", text: "Best burger in the city, no competition. The Spicy Inferno is not for the faint-hearted...", initials: "JA" },
    { name: "Kamola B.", loc: "Mirzo Ulugbek", text: "Ordered via Telegram and it was so easy. Food was fantastic...", initials: "KB" }
  ];

  let cart = [];

  // --- Elements ---
  const grid = document.getElementById('burger-grid');
  const reviewsGrid = document.getElementById('reviews-grid');
  const cartDrawer = document.getElementById('cart-drawer');
  const overlayBg = document.getElementById('overlay-bg');
  const cartCount = document.getElementById('cart-count');
  const cartItemsEl = document.getElementById('cart-items');
  const cartFooterEl = document.getElementById('cart-footer');
  const cartTotalPriceEl = document.getElementById('cart-total-price');
  const menuTabsContainer = document.getElementById('menu-tabs');

  // --- Rendering Functions ---
  function renderBadge(badge, text) {
    if (!badge) return '';
    const cls = badge === 'fire' ? 'badge-fire' : badge === 'chef' ? 'badge-chef' : 'badge-new';
    return `<div class="badge-wrap"><span class="badge ${cls}">${text}</span></div>`;
  }

  function renderBurgerSVG(color) {
    // Sizning original SVG kodingiz (boshqa funksiyalar toza turishi uchun qisqartirib yozmadim, o'zingiznikini qo'yasiz)
    return `<svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="100" cy="158" rx="65" ry="10" fill="rgba(0,0,0,0.25)"/>
      <ellipse cx="100" cy="152" rx="65" ry="14" fill="#c8742a"/>
      <ellipse cx="100" cy="140" rx="65" ry="11" fill="#e8924a"/>
      <rect x="35" y="118" width="130" height="26" rx="6" fill="${color}"/>
      <rect x="39" y="122" width="122" height="18" rx="4" fill="#5c2e12"/>
      <rect x="29" y="110" width="142" height="10" rx="3" fill="#f5b942"/>
      <path d="M30 106 Q55 96 80 106 Q105 96 130 106 Q155 96 170 106" stroke="#4a9e3c" stroke-width="6" stroke-linecap="round" fill="none"/>
      <ellipse cx="78" cy="98" rx="22" ry="7" fill="#e03d2a"/>
      <ellipse cx="128" cy="96" rx="24" ry="7" fill="#e03d2a"/>
      <ellipse cx="100" cy="88" rx="65" ry="11" fill="#c8742a"/>
      <path d="M35 88 Q37 46 100 42 Q163 46 165 88 Z" fill="#d4883a"/>
      <ellipse cx="100" cy="47" rx="46" ry="9" fill="#e8a054"/>
      <ellipse cx="76" cy="56" rx="5" ry="3" fill="#f5c87a" transform="rotate(-20 76 56)"/>
      <ellipse cx="100" cy="50" rx="5" ry="3" fill="#f5c87a" transform="rotate(10 100 50)"/>
      <ellipse cx="124" cy="55" rx="5" ry="3" fill="#f5c87a" transform="rotate(25 124 55)"/>
    </svg>`;
  }

  function renderMenu(filter) {
    const items = filter === 'all' ? menuItems : menuItems.filter(i => i.cat === filter);
    grid.innerHTML = items.map(item => `
      <div class="burger-card" data-id="${item.id}">
        <div class="burger-card-img" style="background:${item.color};">
          ${renderBurgerSVG(item.color === '#2d1a0a' ? '#3d1e0a' : '#5c2e12')}
          ${renderBadge(item.badge, item.badgeText)}
        </div>
        <div class="burger-card-body">
          <h3>${item.name}</h3>
          <p>${item.desc}</p>
          <div class="burger-card-footer">
            <span class="burger-price">${item.price.toLocaleString()} UZS</span>
            <button class="add-btn btn-add-to-cart" data-id="${item.id}">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M12 5v14M5 12h14"/></svg>
              Add
            </button>
          </div>
        </div>
      </div>
    `).join('');
  }

  function renderReviews() {
    reviewsGrid.innerHTML = reviews.map(r => `
      <div class="review-card">
        <div class="review-stars">${'★'.repeat(5).split('').map(() => '<span class="star">★</span>').join('')}</div>
        <p class="review-text">"${r.text}"</p>
        <div class="review-author">
          <div class="author-avatar">${r.initials}</div>
          <div>
            <div class="author-name">${r.name}</div>
            <div class="author-loc">${r.loc}</div>
          </div>
        </div>
        <div class="quote-mark">"</div>
      </div>
    `).join('');
  }

  // --- Cart Logic ---
  function updateCartUI() {
    const total = cart.reduce((s, i) => s + i.price * i.qty, 0);
    const count = cart.reduce((s, i) => s + i.qty, 0);
    
    cartCount.textContent = count;

    if (cart.length === 0) {
      cartItemsEl.innerHTML = '<div class="cart-empty">Your cart is empty. Go pick a burger!</div>';
      cartFooterEl.style.display = 'none';
    } else {
      cartItemsEl.innerHTML = cart.map(i => `
        <div class="cart-item">
          <div>
            <div class="cart-item-name">${i.name} x${i.qty}</div>
            <div style="font-size:12px; color:#888; margin-top:2px;">${i.price.toLocaleString()} UZS each</div>
          </div>
          <div style="display:flex; align-items:center; gap:12px;">
            <span class="cart-item-price">${(i.price * i.qty).toLocaleString()} UZS</span>
            <button class="btn-remove-item" data-id="${i.id}" style="background:none; border:none; color:#E23B2E; cursor:pointer; font-size:18px; line-height:1;">✕</button>
          </div>
        </div>
      `).join('');
      cartFooterEl.style.display = 'block';
      cartTotalPriceEl.textContent = total.toLocaleString() + ' UZS';
    }
  }

  function addToCart(id) {
    const item = menuItems.find(i => i.id === id);
    const existing = cart.find(i => i.id === id);
    if (existing) { 
        existing.qty++; 
    } else { 
        cart.push({ ...item, qty: 1 }); 
    }
    updateCartUI();
    openCart();
  }

  function removeFromCart(id) {
    cart = cart.filter(i => i.id !== id);
    updateCartUI();
    if (cart.length === 0) closeCart();
  }

  // --- Drawer Toggles ---
  function openCart() {
    cartDrawer.classList.add('open');
    overlayBg.classList.add('visible');
    updateCartUI();
  }

  function closeCart() {
    cartDrawer.classList.remove('open');
    overlayBg.classList.remove('visible');
  }

  // --- Event Listeners ---
  
  // Menu Filtering
  menuTabsContainer.addEventListener('click', (e) => {
    if(e.target.classList.contains('menu-tab')) {
      document.querySelectorAll('.menu-tab').forEach(t => t.classList.remove('active'));
      e.target.classList.add('active');
      renderMenu(e.target.dataset.filter);
    }
  });

  // Event Delegation for dynamically generated 'Add to cart' and 'Remove' buttons
  document.addEventListener('click', (e) => {
    // Add to cart
    const addBtn = e.target.closest('.btn-add-to-cart');
    if (addBtn) {
      const id = parseInt(addBtn.dataset.id, 10);
      addToCart(id);
    }

    // Remove from cart
    const removeBtn = e.target.closest('.btn-remove-item');
    if (removeBtn) {
      const id = parseInt(removeBtn.dataset.id, 10);
      removeFromCart(id);
    }

    // Open Cart buttons
    if (e.target.closest('.btn-open-cart')) {
      openCart();
    }
    
    // Close Cart buttons
    if (e.target.closest('.btn-close-cart') || e.target.closest('#overlay-bg')) {
      closeCart();
    }

    // Alerts for mock features
    if (e.target.closest('.btn-book-table')) {
      alert('Reservation system — connect to OpenTable or Resy here.');
    }
    if (e.target.closest('.btn-checkout')) {
      alert('Checkout — connect to your payment system here.');
    }
  });

  // --- Initialization ---
  renderMenu('all');
  renderReviews();
});