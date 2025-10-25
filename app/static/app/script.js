// Cart state
let cart = [];

// Notification queue
let notificationQueue = [];

// Get CSRF token from cookies
function getCSRFToken() {
    let csrfToken = null;
    document.cookie.split(';').forEach(cookie => {
        let [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            csrfToken = value;
        }
    });
    return csrfToken;
}

// Fetch products from API
async function fetchProducts() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/product/trending');
        const products = await response.json();
        const container = document.getElementById('products-container');
        if (container) {
            displayProducts(products);
        }
        await fetchCart(); // Load initial cart state
    } catch (error) {
        console.error('Error fetching products:', error);
    }
}

// Fetch cart items from API
async function fetchCart() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/get/cart', {
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const cartData = await response.json();
        cart = cartData;
        updateCartUI();
    } catch (error) {
        console.error('Error fetching cart:', error);
    }
}

// Display products in grid
function displayProducts(products) {
    const container = document.getElementById('products-container');
    if (!container) return;
    
    container.innerHTML = products.map(product => `
        <div class="window product-card">
            <div class="window-body">
                <img src="http://127.0.0.1:8000${product.image}" alt="${product.name}" class="product-image">
                <div class="product-info">
                    <h3 class="product-name">${product.name}</h3>
                    <p class="product-description">${product.description}</p>
                    <p class="product-price">$ ${product.price}</p>
                    <button class="button add-to-cart-btn" onclick="addToCart(${product.id})">
                        Add to Cart
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Add product to cart
async function addToCart(productId) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/product/add_to_cart/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        await fetchCart(); // Refresh cart from server
        showNotification('Product added to cart successfully!');

    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('Failed to add product to cart. Please try again.', true);
    }
}

// Show notification
function showNotification(message, isError = false) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'window notification-window';
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '1001';
    notification.style.width = '300px';
    notification.style.animation = 'slideIn 0.3s ease-out';

    const titleBar = document.createElement('div');
    titleBar.className = 'title-bar';
    titleBar.innerHTML = `
        <div class="title-bar-text">${isError ? 'Error' : 'Success'}</div>
        <div class="title-bar-controls">
            <button aria-label="Close" onclick="removeNotification(this.parentElement.parentElement.parentElement)"></button>
        </div>
    `;

    const windowBody = document.createElement('div');
    windowBody.className = 'window-body';
    windowBody.style.padding = '1rem';
    windowBody.style.display = 'flex';
    windowBody.style.alignItems = 'center';
    windowBody.style.gap = '1rem';

    const icon = document.createElement('div');
    icon.style.fontSize = '24px';
    icon.innerHTML = isError ? '⚠️' : '✅';

    const messageText = document.createElement('div');
    messageText.textContent = message;
    messageText.style.fontSize = '14px';

    windowBody.appendChild(icon);
    windowBody.appendChild(messageText);

    notification.appendChild(titleBar);
    notification.appendChild(windowBody);

    // Add to queue
    notificationQueue.push(notification);
    document.body.appendChild(notification);

    // Update positions of all notifications
    updateNotificationPositions();

    // Auto-remove after 3 seconds
    setTimeout(() => {
        removeNotification(notification);
    }, 3000);
}

// Remove notification
function removeNotification(notification) {
    const index = notificationQueue.indexOf(notification);
    if (index !== -1) {
        notificationQueue.splice(index, 1);
        notification.remove();
        updateNotificationPositions();
    }
}

// Update positions of all notifications
function updateNotificationPositions() {
    const spacing = 10; // Space between notifications
    const maxNotifications = 3;
    
    // Only keep the last 3 notifications
    while (notificationQueue.length > maxNotifications) {
        const oldestNotification = notificationQueue.shift();
        oldestNotification.remove();
    }

    // Update positions
    notificationQueue.forEach((notification, index) => {
        const bottom = 20 + (index * (notification.offsetHeight + spacing));
        notification.style.bottom = `${bottom}px`;
    });
}

// Update cart UI
function updateCartUI() {
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
        const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
        cartCount.textContent = totalItems;
    }

    const cartContainer = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');
    
    if (cartContainer && cartTotal) {
        if (cart.length === 0) {
            console.log('cart is empty');
            cartContainer.innerHTML = '<div class="empty-cart">Your cart is empty</div>';
            cartTotal.textContent = '$ 0.00:';
            return;
        }

        cartContainer.innerHTML = cart.map(item => `
            <div class="cart-item">
                <img src="${item.image}" alt="${item.name}">
                <div class="cart-item-info">
                    <h3>${item.name}</h3>
                    <p class="cart-item-price">₨ ${item.price}</p>
                </div>
                <div class="quantity-controls">
                    <button class="quantity-btn" onclick="decrementQuantity(${item.product_id})">-</button>
                    <span>${item.quantity}</span>
                    <button class="quantity-btn" onclick="addToCart(${item.product_id})">+</button>
                    <button class="btn" onclick="removeFromCart(${item.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');

        const total = cart.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0);
        cartTotal.textContent = `₨ ${total.toFixed(2)}`;

        // Update checkout button visibility
        const checkoutButton = document.querySelector('.btn-checkout');
        if (checkoutButton) {
            checkoutButton.style.display = cart.length > 0 ? 'block' : 'none';
        }
    }
}

// Decrement item quantity
async function decrementQuantity(productId) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/cart/decrement/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        await fetchCart(); // Refresh cart from server
    } catch (error) {
        console.error('Error updating quantity:', error);
        showNotification('Failed to update quantity. Please try again.', true);
    }
}

// Remove item from cart
async function removeFromCart(cartId) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/delete/cart/${cartId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        await fetchCart(); // Refresh cart from server
    } catch (error) {
        console.error('Error removing item:', error);
        showNotification('Failed to remove item from cart. Please try again.', true);
    }
}

// Initialize eSewa payment
async function initiatePayment() {
    try {
        const total = calculateTotal();
        const response = await fetch(`/api/payment/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ total: total.toFixed(2) })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const payload = await response.json();
        const form = document.getElementById('esewaPaymentForm');
        if (form) {
            for (const key in payload) {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = payload[key];
                }
            }
            form.submit();
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Payment initiation failed. Please try again.', true);
    }
}

function calculateTotal() {
    return cart.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    fetchCart(); // Always fetch cart first
    fetchProducts(); // Then fetch products if on products page
});
