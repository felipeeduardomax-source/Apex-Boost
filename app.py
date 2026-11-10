import os
import re
import json
import uuid
import random
import secrets
import datetime
from urllib.parse import urlsplit
from werkzeug.utils import secure_filename
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, send_from_directory, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, init_db, generate_license_key, is_using_postgres

app = Flask(__name__)

# Security & Session Configuration
is_production = bool(os.environ.get('VERCEL') or os.environ.get('PRODUCTION'))

app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'apex_boost_secret_key_ultra_secure_2026_gamer'),
    SESSION_COOKIE_HTTPONLY=True,        # Previne leitura de cookies via JavaScript (Anti-XSS)
    SESSION_COOKIE_SAMESITE='Lax',       # Proteção contra ataques CSRF
    SESSION_COOKIE_SECURE=is_production, # Cookie apenas via HTTPS em produção
    PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=7),
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,  # Limite de 2MB por requisição (Anti-DoS / Payload)
    DOWNLOAD_FOLDER=os.path.join(os.path.dirname(__file__), 'static', 'downloads')
)

# Ensure DB exists
init_db()

def is_safe_redirect(target):
    """Garante que URLs de redirecionamento sejam estritamente relativas e seguras (Anti-Open-Redirect)"""
    if not target:
        return False
    parts = urlsplit(target)
    if parts.scheme or parts.netloc:
        return False
    if not target.startswith('/') or target.startswith('//') or target.startswith('/\\'):
        return False
    if target in ('/login', '/register', '/logout'):
        return False
    return True

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

    # Determinar usuário ativo para a página solicitada:
    # Se a requisição for no painel admin (/admin*), prioriza o admin logado
    if request.path.startswith('/admin') and session.get('admin_user_id'):
        uid = session.get('admin_user_id')
    else:
        # Nas páginas da vitrine, perfil e checkout, prioriza o cliente comum ou admin fallback
        uid = session.get('user_id') or session.get('admin_user_id')

    logged_user = None
    if uid:
        conn = get_db()
        logged_user = conn.execute(
            "SELECT id, name, email, is_admin, avatar, drop_vip_claimed FROM users WHERE id = ?",
            (uid,)
        ).fetchone()
        conn.close()

    admin_logged = bool(session.get('admin_user_id') or session.get('is_admin'))

    return {
        'cart_count': cart_count,
        'current_user': logged_user,
        'admin_logged': admin_logged,
        'current_year': datetime.datetime.now().year
    }

def is_admin_session():
    """Retorna True se houver uma sessão administrativa autenticada ativa no navegador"""
    return bool(session.get('admin_user_id') or session.get('is_admin'))

# ----------------- ACCESS CONTROL & FIREWALL MIDDLEWARE ----------------- #

BLOCKED_EXTENSIONS = ('.db', '.sqlite', '.sqlite3', '.env', '.py', '.git', '.sh', '.bat', '.sql', '.bak', '.log')
BLOCKED_FILES = {'/.env', '/store.db', '/vercel.json', '/requirements.txt', '/.gitignore', '/procfile'}

@app.before_request
def security_firewall():
    """Firewall de aplicação: bloqueia vazamento de dados confidenciais e força login"""
    path_lower = request.path.lower()

    # 1. Bloquear acesso a arquivos confidenciais do sistema e banco de dados
    if any(path_lower.endswith(ext) for ext in BLOCKED_EXTENSIONS) or path_lower in BLOCKED_FILES:
        abort(403)

    # 2. Bloquear download direto de zips pela pasta estática (deve passar por verificação em /download/)
    if path_lower.startswith('/static/downloads/'):
        abort(403)

    # 3. Bloquear truques de Directory Traversal e injeção de caminho
    if '..' in request.path or '//' in request.path or '\\' in request.path:
        abort(400)

    # 4. Endpoints públicos permitidos sem autenticação
    public_endpoints = {'login', 'register', 'static', 'favicon', 'api_ping'}
    if request.endpoint in public_endpoints or (request.endpoint and request.endpoint.startswith('static')):
        return

    # Arquivos estáticos normais permitidos (css, js, imagens)
    if request.path.startswith('/static/') or request.path in ('/favicon.ico', '/api/ping'):
        return

    # Se for rota administrativa (/admin), exige admin autenticado
    if request.path.startswith('/admin'):
        if not is_admin_session():
            if request.path.startswith('/api/') or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                return jsonify({'error': 'unauthorized', 'message': 'Acesso administrativo restrito.'}), 403
            return redirect(url_for('login', next=request.path))
        return

    # Se não estiver logado nem como cliente nem como admin, redirecionar para login
    if 'user_id' not in session and 'admin_user_id' not in session:
        if request.path in ('/login', '/register', '/favicon.ico', '/api/ping'):
            return

        # Se for requisição API / AJAX / JSON
        if request.path.startswith('/api/') or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'error': 'unauthorized', 'message': 'Faça login para continuar.', 'redirect': url_for('login')}), 401

        # Preservar destino se for rota segura
        next_param = None
        if request.method == 'GET' and request.path not in ('/', '/login', '/register', '/logout'):
            full_p = request.full_path.rstrip('?')
            if is_safe_redirect(full_p):
                next_param = full_p

        return redirect(url_for('login', next=next_param))

@app.after_request
def set_security_headers(response):
    """Aplica cabeçalhos HTTP de segurança e impede cache de dados sensíveis"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    
    # Content-Security-Policy compatível com CDN Bootstrap e Google Fonts
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net data:; "
        "img-src 'self' data: https:; "
        "connect-src 'self';"
    )

    if is_production:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

    # Nunca permitir cache em páginas com dados de pedidos, senhas ou dados do usuário
    sensitive_prefixes = ('/order/', '/admin/')
    if (request.path in ('/profile', '/admin', '/checkout', '/cart') 
        or any(request.path.startswith(p) for p in sensitive_prefixes)):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

    return response

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

# ----------------- AUTHENTICATION ROUTES & PASSWORD PROTECTION ----------------- #

# Lista de senhas comuns que constam em vazamentos públicos mundiais (ex: HaveIBeenPwned / Google Password Checkup)
COMMON_LEAKED_PASSWORDS = {
    '123456', '12345678', '123456789', 'admin123', 'admin', 'password',
    'qwerty', '111111', '123123', 'senha123', 'teste123', 'root', 'master'
}

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Se já logado como cliente comum (sem admin ativo), redireciona para index
    if request.method == 'GET' and 'user_id' in session and not session.get('admin_user_id'):
        if not request.args.get('switch'):
            return redirect(url_for('index'))

    if request.method == 'POST':
        is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if request.is_json:
            data = request.get_json() or {}
            name = data.get('name', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '').strip()
            confirm_password = data.get('confirm_password', '').strip()
        else:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()

        if not name or not email or not password:
            if is_ajax:
                return jsonify({'success': False, 'message': 'Por favor, preencha todos os campos obrigatórios.'}), 400
            flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
            return render_template('register.html', name=name, email=email)

        if len(password) < 6:
            if is_ajax:
                return jsonify({'success': False, 'message': 'A senha deve ter pelo menos 6 caracteres.'}), 400
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return render_template('register.html', name=name, email=email)

        if password.lower() in COMMON_LEAKED_PASSWORDS:
            msg = 'Esta senha é muito fraca e já foi encontrada em vazamentos globais da internet. Por favor, escolha uma senha mais segura.'
            if is_ajax:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'danger')
            return render_template('register.html', name=name, email=email)

        if password != confirm_password:
            if is_ajax:
                return jsonify({'success': False, 'message': 'As senhas não coincidem.'}), 400
            flash('As senhas não coincidem.', 'danger')
            return render_template('register.html', name=name, email=email)

        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            conn.close()
            if is_ajax:
                return jsonify({'success': False, 'message': 'Este e-mail já está cadastrado. Faça login para entrar!'}), 409
            flash('Este email já está cadastrado. Faça login para entrar!', 'warning')
            return redirect(url_for('login', next=request.args.get('next')))

        password_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, is_admin) VALUES (?, ?, ?, 0)",
            (name, email, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Conecta o novo usuário como cliente na vitrine (preserva sessão de admin se ativa)
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email

        flash(f'Conta criada com sucesso! Bem-vindo(a) ao Apex Boost Labs, {name}! 🚀', 'success')
        
        next_url = request.args.get('next')
        redirect_target = url_for('index')
        if is_safe_redirect(next_url):
            redirect_target = next_url
        elif session.get('cart'):
            redirect_target = url_for('checkout')

        if is_ajax:
            return jsonify({
                'success': True,
                'message': f'Conta criada com sucesso, {name}!',
                'redirect_url': redirect_target
            })

        return redirect(redirect_target)

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Se já logado como cliente comum (sem admin ativo), redireciona se for GET
    if request.method == 'GET' and 'user_id' in session and not session.get('admin_user_id'):
        if not request.args.get('switch'):
            return redirect(url_for('index'))

    if request.method == 'POST':
        is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if request.is_json:
            data = request.get_json() or {}
            email = data.get('email', '').strip().lower()
            password = data.get('password', '').strip()
        else:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '').strip()

        if not email or not password:
            if is_ajax:
                return jsonify({'success': False, 'message': 'Informe seu e-mail e sua senha para entrar.'}), 400
            flash('Informe seu e-mail e sua senha para entrar.', 'danger')
            return render_template('login.html', email=email)

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            is_admin_user = bool(user['is_admin'])
            next_url = request.args.get('next')

            if is_admin_user:
                # Armazena credenciais administrativas de forma isolada e persistente
                session['admin_user_id'] = user['id']
                session['admin_name'] = user['name']
                session['admin_email'] = user['email']
                session['is_admin'] = True

                # Se não houver cliente comum logado, preenche a vitrine com o admin para navegação
                if not session.get('user_id'):
                    session['user_id'] = user['id']
                    session['user_name'] = user['name']
                    session['user_email'] = user['email']

                flash(f'Sessão administrativa iniciada! Bem-vindo(a), {user["name"]}! 🛡️', 'success')
                redirect_target = next_url if is_safe_redirect(next_url) else url_for('admin_dashboard')
            else:
                # Login de cliente regular (vitrine / compras)
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                # NOTA DE SEGURANÇA: NÃO removemos session['admin_user_id'] nem deslogamos o admin na outra aba!

                flash(f'Login realizado com sucesso! Bem-vindo(a), {user["name"]}! 🚀', 'success')
                redirect_target = url_for('index')
                if is_safe_redirect(next_url):
                    redirect_target = next_url
                elif session.get('cart'):
                    redirect_target = url_for('checkout')

            if is_ajax:
                return jsonify({
                    'success': True,
                    'message': f'Bem-vindo(a), {user["name"]}!',
                    'redirect_url': redirect_target
                })

            return redirect(redirect_target)
        else:
            if is_ajax:
                return jsonify({'success': False, 'message': 'E-mail ou senha incorretos. Verifique suas credenciais.'}), 401
            flash('E-mail ou senha incorretos. Verifique suas credenciais.', 'danger')
            return render_template('login.html', email=email)

    return render_template('login.html')

@app.route('/logout')
def logout():
    role = request.args.get('role')
    admin_id = session.get('admin_user_id')
    user_id = session.get('user_id')

    # Se for logout de admin ou se a sessão pertencer unicamente ao administrador
    if role == 'admin' or request.path.startswith('/admin') or (admin_id and (not user_id or admin_id == user_id)):
        session.clear()
        flash('Você saiu da sua conta com sucesso.', 'info')
        return redirect(url_for('login'))

    # Se for um cliente diferente saindo da vitrine
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.pop('cart', None)
    session.pop('coupon_code', None)
    session.pop('discount_percent', None)

    # Se não houver sessão administrativa ativa, limpa completamente
    if not session.get('admin_user_id'):
        session.clear()

    flash('Você saiu da sua conta com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/admin/logout')
def admin_logout():
    # Encerra a sessão administrativa
    session.pop('admin_user_id', None)
    session.pop('admin_name', None)
    session.pop('admin_email', None)
    session.pop('is_admin', None)

    # Se a conta da vitrine era a mesma do admin, encerra completamente
    if not session.get('user_id') or session.get('user_id') == session.get('admin_user_id'):
        session.clear()

    flash('Você saiu da sua conta com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    as_admin = request.args.get('as_admin')
    if as_admin and session.get('admin_user_id'):
        user_id = session.get('admin_user_id')
    else:
        user_id = session.get('user_id') or session.get('admin_user_id')

    if not user_id:
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
            elif new_pass.lower() in COMMON_LEAKED_PASSWORDS:
                flash('Esta senha é muito comum e já foi encontrada em vazamentos da internet. Escolha uma senha segura e exclusiva.', 'danger')
            else:
                conn.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (generate_password_hash(new_pass), user_id)
                )
                conn.commit()
                flash('Senha alterada com sucesso! Sua conta está 100% protegida.', 'success')

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
        name = request.form.get('name', '').strip() or session.get('user_name', 'Gamer')
        email = request.form.get('email', '').strip().lower() or session.get('user_email', '')
        payment_method = request.form.get('payment_method', 'PIX')

        # If user not logged in, auto-create or attach account safely
        if not user_id:
            if not name or not email:
                flash('Informe seu nome e e-mail para receber as chaves e downloads.', 'danger')
                conn.close()
                return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal,
                                       discount_amount=discount_amount, total=total, coupon_code=coupon_code)

            existing_user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing_user:
                # Seguranca: NUNCA logar em conta existente sem senha!
                conn.close()
                flash('Este e-mail já possui cadastro. Faça login com sua senha para finalizar sua compra com segurança.', 'warning')
                return redirect(url_for('login', next=url_for('checkout')))
            else:
                # Criar nova conta com senha aleatória segura
                temp_pass = 'Apex' + uuid.uuid4().hex[:8]
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (name, email, password_hash, is_admin) VALUES (?, ?, ?, 0)",
                    (name, email, generate_password_hash(temp_pass))
                )
                user_id = cur.lastrowid
                conn.commit()

            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            session['is_admin'] = 0

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

    # Proteção IDOR: Apenas o dono do pedido ou administrador pode visualizar recibo e chaves
    logged_user_id = session.get('user_id') or session.get('admin_user_id')
    is_admin = is_admin_session()
    if not is_admin and (not logged_user_id or order['user_id'] != logged_user_id):
        conn.close()
        flash('Acesso não autorizado a este pedido.', 'danger')
        return redirect(url_for('index'))

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

# ----------------- DOWNLOAD HANDLER (PROTEGIDO) ----------------- #

@app.route('/download/<filename>')
def download_file(filename):
    user_id = session.get('user_id') or session.get('admin_user_id')
    is_admin = is_admin_session()

    if not user_id and not is_admin:
        flash('Faça login para baixar seus pacotes.', 'warning')
        return redirect(url_for('login', next=request.path))

    safe_name = os.path.basename(filename)
    safe_files = {
        'starter_pack.zip',
        'ultra_fps_pack.zip',
        'network_pro_pack.zip',
        'ultimate_extreme_suite.zip'
    }
    if safe_name not in safe_files:
        abort(404)

    # Validação de compra: Apenas admin ou comprador com pedido PAGO pode baixar
    if not is_admin:
        conn = get_db()
        purchased = conn.execute("""
            SELECT 1 FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE o.user_id = ? AND o.status = 'PAGO' AND p.download_file = ?
        """, (user_id, safe_name)).fetchone()
        conn.close()

        if not purchased:
            flash('Você precisa adquirir este pacote para realizar o download.', 'danger')
            return redirect(url_for('index') + '#tab-packs')

    filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], safe_name)
    if not os.path.exists(filepath):
        abort(404)

    return send_from_directory(
        app.config['DOWNLOAD_FOLDER'],
        safe_name,
        as_attachment=True,
        download_name=safe_name
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

# ----------------- ADMIN DASHBOARD & STORE MANAGEMENT ----------------- #

@app.route('/admin')
def admin_dashboard():
    if not is_admin_session():
        flash('Acesso restrito para administradores.', 'danger')
        return redirect(url_for('login', next=request.path))

    conn = get_db()
    try:
        total_sales_row = conn.execute("SELECT COALESCE(SUM(total), 0) as total FROM orders WHERE status = 'PAGO'").fetchone()
        total_sales = float(total_sales_row['total']) if total_sales_row and total_sales_row['total'] is not None else 0.0

        total_orders_row = conn.execute("SELECT COUNT(*) as cnt FROM orders").fetchone()
        total_orders = total_orders_row['cnt'] if total_orders_row else 0

        paid_orders_row = conn.execute("SELECT COUNT(*) as cnt FROM orders WHERE status = 'PAGO'").fetchone()
        paid_orders = paid_orders_row['cnt'] if paid_orders_row else 0

        total_users_row = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
        total_users = total_users_row['cnt'] if total_users_row else 0

        total_products_row = conn.execute("SELECT COUNT(*) as cnt FROM products").fetchone()
        total_products = total_products_row['cnt'] if total_products_row else 0

        # Estatísticas inteligentes
        ticket_medio = (total_sales / paid_orders) if paid_orders > 0 else 0.0
        taxa_conversao = (paid_orders / total_orders * 100) if total_orders > 0 else 0.0

        # Produto campeão de vendas
        top_prod_row = conn.execute("""
            SELECT p.name, COUNT(oi.id) as sales_count
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status = 'PAGO'
            GROUP BY p.name
            ORDER BY sales_count DESC LIMIT 1
        """).fetchone()
        top_product_name = top_prod_row['name'] if top_prod_row else "Aguardando Vendas"

        # Vendas por produto (Gráfico de performance)
        sales_by_product_raw = conn.execute("""
            SELECT p.name, p.tag, COALESCE(SUM(oi.price), 0) as total_revenue, COUNT(oi.id) as sales_count
            FROM products p
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id AND o.status = 'PAGO'
            GROUP BY p.id, p.name, p.tag
            ORDER BY total_revenue DESC
        """).fetchall()
        sales_by_product = []
        for s in sales_by_product_raw:
            s_dict = dict(s)
            s_dict['total_revenue'] = float(s_dict.get('total_revenue') or 0.0)
            sales_by_product.append(s_dict)

        recent_orders = conn.execute("""
            SELECT o.*, u.name as user_name, u.email as user_email
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
            ORDER BY o.id DESC LIMIT 25
        """).fetchall()

        products = conn.execute("SELECT * FROM products ORDER BY id ASC").fetchall()
        users = conn.execute("SELECT id, name, email, is_admin, created_at FROM users ORDER BY id DESC LIMIT 25").fetchall()
        coupons = conn.execute("SELECT * FROM coupons ORDER BY id DESC").fetchall()
    finally:
        conn.close()

    db_backend = "Neon PostgreSQL (Nuvem)" if is_using_postgres() else "SQLite (Local)"

    return render_template(
        'admin.html',
        total_sales=total_sales,
        total_orders=total_orders,
        paid_orders=paid_orders,
        ticket_medio=ticket_medio,
        taxa_conversao=taxa_conversao,
        top_product_name=top_product_name,
        sales_by_product=sales_by_product,
        total_users=total_users,
        total_products=total_products,
        recent_orders=recent_orders,
        products=products,
        users=users,
        coupons=coupons,
        db_backend=db_backend
    )

@app.route('/admin/add-product', methods=['POST'])
def admin_add_product():
    if not is_admin_session():
        abort(403)

    name = request.form.get('name', '').strip()
    if not name:
        flash('O nome do produto é obrigatório.', 'danger')
        return redirect(url_for('admin_dashboard'))

    tag = request.form.get('tag', '').strip() or 'Otimização Gamer'
    badge = request.form.get('badge', '').strip() or 'NOVO'
    short_desc = request.form.get('short_desc', '').strip() or 'Pack de otimização de alta performance.'
    description = request.form.get('description', '').strip() or short_desc
    fps_gain = request.form.get('fps_gain', '').strip() or '+50% FPS'
    latency_drop = request.form.get('latency_drop', '').strip() or '-30ms Delay'
    download_file = request.form.get('download_file', '').strip() or 'ultra_fps_pack.zip'
    icon = request.form.get('icon', '').strip() or 'bi-lightning-charge-fill'

    try:
        price = float(request.form.get('price', 19.90))
    except (ValueError, TypeError):
        price = 19.90

    try:
        old_price_val = request.form.get('old_price', '').strip()
        old_price = float(old_price_val) if old_price_val else None
    except (ValueError, TypeError):
        old_price = None

    raw_features = request.form.get('features', '').strip()
    if raw_features:
        features_list = [f.strip() for f in raw_features.split('\n') if f.strip()]
    else:
        features_list = [
            "Otimização completa em 1 clique",
            "Script automático com backup seguro",
            "Redução imediata de latência e input lag",
            "Suporte vitalício e atualizações"
        ]
    features_json = json.dumps(features_list)

    base_slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    if not base_slug:
        base_slug = f"pack-{random.randint(1000, 9999)}"
    slug = base_slug

    conn = get_db()
    try:
        existing = conn.execute("SELECT id FROM products WHERE slug = ?", (slug,)).fetchone()
        if existing:
            slug = f"{base_slug}-{random.randint(100, 999)}"

        conn.execute("""
            INSERT INTO products (
                slug, name, tag, short_desc, description,
                price, old_price, badge, fps_gain, latency_drop,
                features, download_file, icon, popular, active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 1)
        """, (
            slug, name, tag, short_desc, description,
            price, old_price, badge, fps_gain, latency_drop,
            features_json, download_file, icon
        ))
        conn.commit()
        flash(f'Produto "{name}" cadastrado com sucesso no catálogo!', 'success')
    except Exception as e:
        flash(f'Erro ao cadastrar produto: {str(e)}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-product/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    if not is_admin_session():
        abort(403)
    conn = get_db()
    try:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        flash('Produto excluído com sucesso do catálogo!', 'info')
    except Exception as e:
        flash(f'Erro ao excluir produto: {str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle-product/<int:product_id>', methods=['GET', 'POST'])
def admin_toggle_product(product_id):
    if not is_admin_session():
        abort(403)
    conn = get_db()
    conn.execute("UPDATE products SET active = CASE WHEN active = 1 THEN 0 ELSE 1 END WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    flash('Status do produto atualizado!', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add-coupon', methods=['POST'])
def admin_add_coupon():
    if not is_admin_session():
        abort(403)
    code = request.form.get('code', '').strip().upper()
    try:
        discount = int(request.form.get('discount', 10))
        if discount < 1 or discount > 100:
            discount = 10
    except (ValueError, TypeError):
        discount = 10

    if code:
        conn = get_db()
        try:
            conn.execute("INSERT INTO coupons (code, discount_percent) VALUES (?, ?)", (code, discount))
            conn.commit()
            flash(f'Cupom {code} criado com sucesso!', 'success')
        except Exception:
            flash('Erro: cupom já existente.', 'danger')
        finally:
            conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-coupon/<int:coupon_id>', methods=['POST'])
def admin_delete_coupon(coupon_id):
    if not is_admin_session():
        abort(403)
    conn = get_db()
    try:
        conn.execute("DELETE FROM coupons WHERE id = ?", (coupon_id,))
        conn.commit()
        flash('Cupom removido com sucesso!', 'info')
    except Exception as e:
        flash(f'Erro ao remover cupom: {str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle-order-status/<int:order_id>', methods=['POST'])
def admin_toggle_order_status(order_id):
    if not is_admin_session():
        abort(403)
    conn = get_db()
    try:
        order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if order:
            new_status = 'PENDENTE' if order['status'] == 'PAGO' else 'PAGO'
            conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
            if new_status == 'PAGO':
                items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
                for item in items:
                    if not item['license_key']:
                        new_key = generate_license_key()
                        conn.execute("UPDATE order_items SET license_key = ? WHERE id = ?", (new_key, item['id']))
            conn.commit()
            flash(f'Status do pedido #{order["order_code"]} alterado para {new_status}!', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar pedido: {str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/clear-orders', methods=['POST'])
def admin_clear_orders():
    if not is_admin_session():
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

@app.route('/api/claim-drop', methods=['POST'])
def claim_drop():
    """Resgate único do Drop VIP para usuários logados"""
    user_id = session.get('user_id') or session.get('admin_user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'Você precisa estar logado para resgatar seu Drop VIP!',
            'redirect': url_for('login')
        }), 401

    conn = get_db()
    try:
        user = conn.execute("SELECT id, drop_vip_claimed FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado.'}), 404

        u_dict = dict(user)
        if u_dict.get('drop_vip_claimed'):
            return jsonify({
                'success': False,
                'already_claimed': True,
                'message': 'Você já resgatou o seu Drop VIP exclusivo de boas-vindas nesta conta.'
            }), 400

        # Marca como resgatado no banco de dados de forma definitiva
        conn.execute("UPDATE users SET drop_vip_claimed = 1 WHERE id = ?", (user_id,))
        conn.commit()

        # Ativa o cupom de 20% OFF automaticamente na sessão do usuário
        session['coupon_code'] = 'PRIMEIRACOMPRA'
        session['discount_percent'] = 20.0
        session.modified = True

        return jsonify({
            'success': True,
            'coupon': 'PRIMEIRACOMPRA',
            'discount': 20,
            'message': 'Drop Lendário desbloqueado! Cupom PRIMEIRACOMPRA (20% OFF) aplicado automaticamente.'
        })
    finally:
        conn.close()

@app.route('/api/drop-status')
def drop_status():
    """Retorna o status do Drop VIP do usuário logado"""
    user_id = session.get('user_id') or session.get('admin_user_id')
    if not user_id:
        return jsonify({'logged_in': False, 'claimed': False})
    conn = get_db()
    try:
        user = conn.execute("SELECT drop_vip_claimed FROM users WHERE id = ?", (user_id,)).fetchone()
        claimed = bool(dict(user).get('drop_vip_claimed')) if user else False
        return jsonify({'logged_in': True, 'claimed': claimed})
    finally:
        conn.close()

# ----------------- CUSTOM ERROR HANDLERS (ANTI-LEAK) ----------------- #

@app.errorhandler(400)
def bad_request_error(e):
    return render_template(
        'error.html',
        error_code=400,
        error_badge="REQUISIÇÃO INVÁLIDA",
        error_title="400 - Parâmetros Incorretos",
        error_message="A requisição enviada contém caracteres ou parâmetros inválidos."
    ), 400

@app.errorhandler(403)
def forbidden_error(e):
    return render_template(
        'error.html',
        error_code=403,
        error_badge="ACESSO BLOQUEADO",
        error_title="403 - Acesso Negado",
        error_message="Você não possui permissão para acessar este recurso ou baixar este arquivo diretamente."
    ), 403

@app.errorhandler(404)
def not_found_error(e):
    return render_template(
        'error.html',
        error_code=404,
        error_badge="NÃO ENCONTRADO",
        error_title="404 - Página Não Encontrada",
        error_message="O endereço solicitado não existe, foi movido ou está temporariamente indisponível."
    ), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"[SECURITY] Erro 500 interceptado: {e}")
    return render_template(
        'error.html',
        error_code=500,
        error_badge="INSTABILIDADE TEMPORÁRIA",
        error_title="500 - Instabilidade nos Servidores",
        error_message="Nossos sistemas de segurança já isolaram o incidente. Nenhum dado foi afetado. Tente novamente em instantes."
    ), 500

# ----------------- RUN SCRIPT ----------------- #

if __name__ == '__main__':
    print("==================================================")
    print("      🚀 APEX BOOST LABS - LOJA ONLINE ATIVA      ")
    print("  Acesse no navegador: http://127.0.0.1:5000       ")
    print("  Servidor seguro com proteções ativas.           ")
    print("==================================================")
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)

