import os
import json
import uuid
import datetime
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, send_from_directory, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, init_db, generate_license_key, is_using_postgres

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'apex_boost_secret_key_ultra_secure_2026_gamer')
app.config['DOWNLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'downloads')

# Ensure DB exists
init_db()

# Jinja template filters for robust date formatting across SQLite and Neon PostgreSQL
@app.template_filter('format_datetime')
def format_datetime_filter(value, fmt='%d/%m/%Y %H:%M'):
    if not value:
        return ''
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.strftime(fmt)
    val_str = str(value)
    try:
        clean_str = val_str.replace('T', ' ')[:19]
        dt = datetime.datetime.strptime(clean_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime(fmt)
    except Exception:
        return val_str[:16]

@app.template_filter('format_date')
def format_date_filter(value, fmt='%d/%m/%Y'):
    return format_datetime_filter(value, fmt=fmt)

def get_cart():
    """Retorna o carrinho da sessão formatado de forma sanitizada como dict {prod_id_str: qty}"""
    raw_cart = session.get('cart', {})
    if isinstance(raw_cart, dict):
        return raw_cart
    elif isinstance(raw_cart, (list, tuple, set)):
        normalized = {}
        for item in raw_cart:
            normalized[str(item)] = 1
        session['cart'] = normalized
        session.modified = True
        return normalized
    session['cart'] = {}
    session.modified = True
    return {}

# Context processor for templates
@app.context_processor
def inject_global_data():
    cart = get_cart()
    cart_count = sum(cart.values()) if isinstance(cart, dict) else 0
    logged_user = None
    if 'user_id' in session:
        conn = get_db()
        logged_user = conn.execute(
            "SELECT id, name, email, is_admin, avatar FROM users WHERE id = ?",
            (session['user_id'],)
        ).fetchone()
        conn.close()
    return {
        'cart_count': cart_count,
        'current_user': logged_user,
        'current_year': datetime.datetime.now().year
    }

# ----------------- ACCESS CONTROL MIDDLEWARE ----------------- #

@app.before_request
def require_login():
    """Requires user to be logged in before accessing the site"""
    public_endpoints = {'login', 'register', 'static', 'favicon', 'api_ping'}
    if request.endpoint in public_endpoints or (request.endpoint and request.endpoint.startswith('static')):
        return

    # Direct static file requests
    if request.path.startswith('/static/') or request.path in ('/favicon.ico', '/api/ping'):
        return

    # If unauthenticated, redirect to login
    if 'user_id' not in session:
        if request.path in ('/login', '/register', '/favicon.ico', '/api/ping'):
            return

        # If AJAX / JSON request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'error': 'unauthorized', 'message': 'Faça login para continuar.', 'redirect': url_for('login')}), 401

        # Preserve query or path for redirect after login
        next_param = None
        if request.method == 'GET' and request.path not in ('/', '/login', '/register', '/logout'):
            next_param = request.full_path.rstrip('?')

        return redirect(url_for('login', next=next_param))

# ----------------- HOME & CATALOG ROUTES ----------------- #

@app.route('/')
def index():
    conn = get_db()
    products = conn.execute("SELECT * FROM products WHERE active = 1 ORDER BY popular DESC, price ASC").fetchall()
    reviews = conn.execute("SELECT * FROM reviews ORDER BY id DESC").fetchall()
    
    # Parse features json for each product and guarantee float prices
    prods_list = []
    for p in products:
        item = dict(p)
        item['price'] = float(item.get('price') or 0.0)
        if item.get('old_price') is not None:
            item['old_price'] = float(item['old_price'])
        item['features_list'] = json.loads(item['features']) if item['features'] else []
        prods_list.append(item)
        
    conn.close()
    return render_template('index.html', products=prods_list, reviews=reviews)

@app.route('/pack/<slug>')
def product_detail(slug):
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE slug = ? AND active = 1", (slug,)).fetchone()
    if not product:
        conn.close()
        abort(404)
        
    p_dict = dict(product)
    p_dict['price'] = float(p_dict.get('price') or 0.0)
    if p_dict.get('old_price') is not None:
        p_dict['old_price'] = float(p_dict['old_price'])
    p_dict['features_list'] = json.loads(p_dict['features']) if p_dict['features'] else []
    
    # Related products
    other_products_raw = conn.execute(
        "SELECT * FROM products WHERE id != ? AND active = 1 LIMIT 3", (product['id'],)
    ).fetchall()
    other_products = []
    for op in other_products_raw:
        op_dict = dict(op)
        op_dict['price'] = float(op_dict.get('price') or 0.0)
        if op_dict.get('old_price') is not None:
            op_dict['old_price'] = float(op_dict['old_price'])
        other_products.append(op_dict)
    
    # Product reviews
    reviews = conn.execute("SELECT * FROM reviews ORDER BY id DESC LIMIT 4").fetchall()
    conn.close()
    
    return render_template('product.html', product=p_dict, other_products=other_products, reviews=reviews)

# ----------------- AUTHENTICATION ROUTES ----------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not name or not email or not password:
            flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
            return render_template('register.html', name=name, email=email)

        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return render_template('register.html', name=name, email=email)

        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('register.html', name=name, email=email)

        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            conn.close()
            flash('Este email já está cadastrado. Faça login para entrar!', 'warning')
            return redirect(url_for('login', next=request.args.get('next')))

        password_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Log in user automatically
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email
        session['is_admin'] = 0

        flash(f'Conta criada com sucesso! Bem-vindo(a) ao Apex Boost Labs, {name}! 🚀', 'success')
        
        next_url = request.args.get('next')
        if next_url and next_url.startswith('/') and next_url not in ('/login', '/register'):
            return redirect(next_url)
        if session.get('cart'):
            return redirect(url_for('checkout'))
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Informe seu e-mail e sua senha para entrar.', 'danger')
            return render_template('login.html', email=email)

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['is_admin'] = bool(user['is_admin'])

            flash(f'Login realizado com sucesso! Bem-vindo(a), {user["name"]}! 🚀', 'success')
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/') and next_url not in ('/login', '/register'):
                return redirect(next_url)
            if session.get('cart'):
                return redirect(url_for('checkout'))
            return redirect(url_for('index'))
        else:
            flash('E-mail ou senha incorretos. Verifique suas credenciais.', 'danger')
            return render_template('login.html', email=email)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.pop('is_admin', None)
    flash('Você saiu da sua conta com sucesso. Faça login novamente para acessar o site.', 'info')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Faça login para acessar o painel de membro.', 'warning')
        return redirect(url_for('login', next=request.path))

    user_id = session['user_id']
    conn = get_db()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            name = request.form.get('name', '').strip()
            if name:
                conn.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
                conn.commit()
                session['user_name'] = name
                flash('Nome atualizado com sucesso!', 'success')
        elif action == 'change_password':
            old_pass = request.form.get('old_password', '')
            new_pass = request.form.get('new_password', '')
            user = conn.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
            if not check_password_hash(user['password_hash'], old_pass):
                flash('Senha atual incorreta.', 'danger')
            elif len(new_pass) < 6:
                flash('A nova senha deve ter no mínimo 6 caracteres.', 'danger')
            else:
                conn.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (generate_password_hash(new_pass), user_id)
                )
                conn.commit()
                flash('Senha alterada com sucesso!', 'success')

    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    
    # Get user orders
    orders = conn.execute("""
        SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC
    """, (user_id,)).fetchall()

    # Get user purchased items & licenses for downloads
    purchased_items = conn.execute("""
        SELECT oi.*, p.name as prod_name, p.slug as prod_slug, p.download_file, p.icon, o.order_code, o.created_at as purchase_date
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN products p ON oi.product_id = p.id
        WHERE o.user_id = ? AND o.status = 'PAGO'
        ORDER BY oi.id DESC
    """, (user_id,)).fetchall()

    conn.close()
    return render_template('profile.html', user=user, orders=orders, purchased_items=purchased_items)

# ----------------- CART & CHECKOUT ROUTES ----------------- #

@app.route('/cart')
def view_cart():
    cart = get_cart()
    cart_items = []
    subtotal = 0.0

    if cart:
        conn = get_db()
        for prod_id_str, qty in list(cart.items()):
            try:
                p_id = int(prod_id_str)
                p_qty = int(qty)
            except (ValueError, TypeError):
                continue
            prod = conn.execute("SELECT * FROM products WHERE id = ?", (p_id,)).fetchone()
            if prod:
                p_dict = dict(prod)
                price = float(p_dict.get('price') or 0.0)
                p_dict['price'] = price
                p_dict['quantity'] = p_qty
                p_dict['item_total'] = round(price * p_qty, 2)
                subtotal += p_dict['item_total']
                cart_items.append(p_dict)
        conn.close()

    subtotal = round(subtotal, 2)
    discount_percent = float(session.get('discount_percent', 0) or 0)
    coupon_code = session.get('coupon_code', '')
    discount_amount = round((subtotal * discount_percent) / 100.0, 2)
    total = max(0.0, round(subtotal - discount_amount, 2))

    return render_template(
        'cart.html',
        cart_items=cart_items,
        subtotal=subtotal,
        discount_amount=discount_amount,
        discount_percent=discount_percent,
        coupon_code=coupon_code,
        total=total
    )

@app.route('/cart/add/<int:product_id>', methods=['POST', 'GET'])
def add_to_cart(product_id):
    conn = get_db()
    product = conn.execute("SELECT id, name FROM products WHERE id = ? AND active = 1", (product_id,)).fetchone()
    conn.close()

    if not product:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Produto não encontrado.'}), 404
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('index'))

    cart = get_cart()
    str_id = str(product_id)
    cart[str_id] = 1
    session['cart'] = cart
    session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('format') == 'json':
        return jsonify({
            'success': True,
            'message': f'{product["name"]} adicionado ao carrinho!',
            'cart_count': sum(cart.values())
        })

    flash(f'{product["name"]} adicionado ao seu carrinho!', 'success')
    return redirect(url_for('view_cart'))

@app.route('/cart/remove/<int:product_id>')
def remove_from_cart(product_id):
    cart = get_cart()
    str_id = str(product_id)
    if str_id in cart:
        del cart[str_id]
        session['cart'] = cart
        session.modified = True
        flash('Item removido do carrinho.', 'info')

    if not cart:
        session.pop('coupon_code', None)
        session.pop('discount_percent', None)

    return redirect(url_for('view_cart'))

@app.route('/cart/clear')
def clear_cart():
    session.pop('cart', None)
    session.pop('coupon_code', None)
    session.pop('discount_percent', None)
    flash('Seu carrinho foi esvaziado.', 'info')
    return redirect(url_for('view_cart'))

@app.route('/cart/apply-coupon', methods=['POST'])
def apply_coupon():
    code = request.form.get('coupon_code', '').strip().upper()
    if not code:
        flash('Digite um código de cupom.', 'warning')
        return redirect(url_for('view_cart'))

    conn = get_db()
    coupon = conn.execute("SELECT * FROM coupons WHERE code = ? AND active = 1", (code,)).fetchone()
    conn.close()

    if coupon:
        session['coupon_code'] = coupon['code']
        session['discount_percent'] = float(coupon['discount_percent'])
        flash(f'Cupom {coupon["code"]} aplicado! Desconto de {coupon["discount_percent"]}% concedido.', 'success')
    else:
        flash('Cupom inválido ou expirado. Tente FPSBOOST ou PRIMEIRACOMPRA.', 'danger')

    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = get_cart()
    if not cart:
        flash('Seu carrinho está vazio. Adicione um pack antes de finalizar.', 'warning')
        return redirect(url_for('index'))

    # Calculate cart total
    conn = get_db()
    cart_items = []
    subtotal = 0.0
    for prod_id_str, qty in list(cart.items()):
        try:
            p_id = int(prod_id_str)
            p_qty = int(qty)
        except (ValueError, TypeError):
            continue
        prod = conn.execute("SELECT * FROM products WHERE id = ?", (p_id,)).fetchone()
        if prod:
            p_dict = dict(prod)
            price = float(p_dict.get('price') or 0.0)
            p_dict['price'] = price
            p_dict['quantity'] = p_qty
            p_dict['item_total'] = round(price * p_qty, 2)
            subtotal += p_dict['item_total']
            cart_items.append(p_dict)

    subtotal = round(subtotal, 2)
    discount_percent = float(session.get('discount_percent', 0) or 0)
    coupon_code = session.get('coupon_code', None)
    discount_amount = round((subtotal * discount_percent) / 100.0, 2)
    total = max(0.0, round(subtotal - discount_amount, 2))

    if request.method == 'POST':
        # Process order
        user_id = session.get('user_id')
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        payment_method = request.form.get('payment_method', 'PIX')

        # If user not logged in, auto-create or attach account
        if not user_id:
            if not name or not email:
                flash('Informe seu nome e e-mail para receber as chaves e downloads.', 'danger')
                conn.close()
                return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal,
                                       discount_amount=discount_amount, total=total, coupon_code=coupon_code)

            existing_user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing_user:
                user_id = existing_user['id']
            else:
                # Create an account with a default password and email notice
                temp_pass = 'Apex' + uuid.uuid4().hex[:6]
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, generate_password_hash(temp_pass))
                )
                user_id = cur.lastrowid
                conn.commit()

            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email

        # Generate unique order code (e.g. APX-94821)
        order_code = f"APX-{datetime.datetime.now().strftime('%m%d')}-{uuid.uuid4().hex[:5].upper()}"

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (order_code, user_id, customer_name, customer_email, total, discount, coupon_used, payment_method, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PAGO')
        """, (order_code, user_id, name, email, total, discount_amount, coupon_code, payment_method))
        order_id = cursor.lastrowid

        # Insert order items and generate licenses
        for item in cart_items:
            license_key = generate_license_key()
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, product_name, price, license_key)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, item['id'], item['name'], item['price'], license_key))

        conn.commit()
        conn.close()

        # Clear cart and coupon
        session.pop('cart', None)
        session.pop('coupon_code', None)
        session.pop('discount_percent', None)

        flash('Pagamento aprovado instantaneamente! Seus packs e licenças estão prontos para download.', 'success')
        return redirect(url_for('order_success', order_code=order_code))

    conn.close()
    return render_template(
        'checkout.html',
        cart_items=cart_items,
        subtotal=subtotal,
        discount_amount=discount_amount,
        discount_percent=discount_percent,
        coupon_code=coupon_code,
        total=total
    )

@app.route('/order/<order_code>')
def order_success(order_code):
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE order_code = ?", (order_code,)).fetchone()
    if not order:
        conn.close()
        abort(404)

    o_dict = dict(order)
    o_dict['total'] = float(o_dict.get('total') or 0.0)
    if o_dict.get('discount') is not None:
        o_dict['discount'] = float(o_dict['discount'])

    raw_items = conn.execute("""
        SELECT oi.*, p.download_file, p.slug as prod_slug, p.icon
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    """, (order['id'],)).fetchall()
    conn.close()

    items = []
    for it in raw_items:
        it_dict = dict(it)
        it_dict['price'] = float(it_dict.get('price') or 0.0)
        items.append(it_dict)

    return render_template('order_success.html', order=o_dict, items=items)

# ----------------- DOWNLOAD HANDLER ----------------- #

@app.route('/download/<filename>')
def download_file(filename):
    # Only allow files from safe list
    safe_files = ['starter_pack.zip', 'ultra_fps_pack.zip', 'network_pro_pack.zip', 'ultimate_extreme_suite.zip']
    if filename not in safe_files:
        abort(404)

    # If user is logged in or has an active order, allow download
    filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        abort(404)

    return send_from_directory(
        app.config['DOWNLOAD_FOLDER'],
        filename,
        as_attachment=True,
        download_name=filename
    )

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'img'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/api/ping')
def api_ping():
    return jsonify({
        'status': 'ok',
        'server_time': datetime.datetime.now().isoformat()
    })

# ----------------- ADMIN DASHBOARD ----------------- #

@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('Acesso restrito para administradores.', 'danger')
        return redirect(url_for('login', next=request.path))

    conn = get_db()
    try:
        total_sales_row = conn.execute("SELECT COALESCE(SUM(total), 0) as total FROM orders WHERE status = 'PAGO'").fetchone()
        total_sales = float(total_sales_row['total']) if total_sales_row and total_sales_row['total'] is not None else 0.0

        total_orders_row = conn.execute("SELECT COUNT(*) as cnt FROM orders").fetchone()
        total_orders = total_orders_row['cnt'] if total_orders_row else 0

        total_users_row = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
        total_users = total_users_row['cnt'] if total_users_row else 0

        total_products_row = conn.execute("SELECT COUNT(*) as cnt FROM products").fetchone()
        total_products = total_products_row['cnt'] if total_products_row else 0

        recent_orders = conn.execute("""
            SELECT o.*, u.name as user_name, u.email as user_email
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
            ORDER BY o.id DESC LIMIT 15
        """).fetchall()

        products = conn.execute("SELECT * FROM products ORDER BY id ASC").fetchall()
        users = conn.execute("SELECT id, name, email, is_admin, created_at FROM users ORDER BY id DESC LIMIT 20").fetchall()
        coupons = conn.execute("SELECT * FROM coupons ORDER BY id DESC").fetchall()
    finally:
        conn.close()

    db_backend = "Neon PostgreSQL (Nuvem)" if is_using_postgres() else "SQLite (Local)"

    return render_template(
        'admin.html',
        total_sales=total_sales,
        total_orders=total_orders,
        total_users=total_users,
        total_products=total_products,
        recent_orders=recent_orders,
        products=products,
        users=users,
        coupons=coupons,
        db_backend=db_backend
    )

@app.route('/admin/toggle-product/<int:product_id>')
def admin_toggle_product(product_id):
    if not session.get('is_admin'):
        abort(403)
    conn = get_db()
    conn.execute("UPDATE products SET active = CASE WHEN active = 1 THEN 0 ELSE 1 END WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    flash('Status do produto atualizado!', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add-coupon', methods=['POST'])
def admin_add_coupon():
    if not session.get('is_admin'):
        abort(403)
    code = request.form.get('code', '').strip().upper()
    discount = request.form.get('discount', 10)
    if code:
        conn = get_db()
        try:
            conn.execute("INSERT INTO coupons (code, discount_percent) VALUES (?, ?)", (code, int(discount)))
            conn.commit()
            flash(f'Cupom {code} criado com sucesso!', 'success')
        except Exception:
            flash('Erro: cupom já existente.', 'danger')
        conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/clear-orders', methods=['POST'])
def admin_clear_orders():
    if not session.get('is_admin'):
        abort(403)
    conn = get_db()
    conn.execute("DELETE FROM order_items")
    conn.execute("DELETE FROM orders")
    conn.commit()
    conn.close()
    flash('Histórico de pedidos e faturamento zerado com sucesso!', 'success')
    return redirect(url_for('admin_dashboard'))

# ----------------- API HELPER ROUTES ----------------- #

@app.route('/api/live-sales')
def live_sales():
    """Generates simulated realistic gamer buyer notifications for social proof toast"""
    notifications = [
        {"buyer": "Matheus S. (RJ)", "pack": "Competitive FPS Ultra Pack", "time": "há 3 minutos"},
        {"buyer": "Lucas F. (SP)", "pack": "Ultimate Extreme Suite", "time": "há 7 minutos"},
        {"buyer": "Thiago M. (MG)", "pack": "Starter Tweak Pack", "time": "há 12 minutos"},
        {"buyer": "Pedro H. (PR)", "pack": "Zero Latency & Network Pro", "time": "há 18 minutos"},
        {"buyer": "Rafael B. (RS)", "pack": "Ultimate Extreme Suite", "time": "há 24 minutos"},
        {"buyer": "Bruno C. (SC)", "pack": "Competitive FPS Ultra Pack", "time": "há 29 minutos"}
    ]
    return jsonify(notifications)

# ----------------- RUN SCRIPT ----------------- #

if __name__ == '__main__':
    print("==================================================")
    print("      🚀 APEX BOOST LABS - LOJA ONLINE ATIVA      ")
    print("  Acesse no navegador: http://127.0.0.1:5000       ")
    print("  Conta Admin: admin@apexboost.com / admin123    ")
    print("  Conta Gamer: gamer@teste.com / 123456          ")
    print("==================================================")
    app.run(debug=True, host='0.0.0.0', port=5000)

