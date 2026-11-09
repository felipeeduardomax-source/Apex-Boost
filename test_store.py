import unittest
import json
from app import app
from database import init_db, get_db

class StoreTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        init_db()

    def test_01_index_page_and_gateway(self):
        # 1. Unauthenticated request to / should redirect to /login
        res_guest = self.client.get('/')
        self.assertEqual(res_guest.status_code, 302)
        self.assertIn('/login', res_guest.headers.get('Location', ''))

        # 2. Login with valid account
        self.client.post('/login', data={
            'email': 'gamer@teste.com',
            'password': '123456'
        })

        # 3. Authenticated access to / succeeds with 200 OK and loads store
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'APEX', response.data)
        self.assertIn(b'BOOST', response.data)
        self.assertIn(b'Competitive FPS Ultra Pack', response.data)

    def test_02_product_detail(self):
        # Log in first
        self.client.post('/login', data={
            'email': 'gamer@teste.com',
            'password': '123456'
        })
        response = self.client.get('/pack/ultra-fps-competitive-pack')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Competitive FPS Ultra Pack', response.data)

    def test_03_registration_and_login(self):
        # Register new gamer
        test_email = "testgamer@domain.com"
        conn = get_db()
        conn.execute("DELETE FROM users WHERE email = ?", (test_email,))
        conn.commit()
        conn.close()

        res_reg = self.client.post('/register', data={
            'name': 'Gamer de Teste',
            'email': test_email,
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(res_reg.status_code, 200)
        self.assertIn(b'Conta criada com sucesso', res_reg.data)

        # Logout redirects to login
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)
        self.assertIn(b'ENTRAR NA CONTA', res_logout.data)

        # Login redirects to home page / site
        res_login = self.client.post('/login', data={
            'email': test_email,
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Login realizado com sucesso', res_login.data)
        self.assertIn(b'Competitive FPS Ultra Pack', res_login.data)

    def test_04_cart_and_coupon(self):
        # Log in first
        self.client.post('/login', data={
            'email': 'gamer@teste.com',
            'password': '123456'
        })

        # Add product 1 to cart
        res_add = self.client.get('/cart/add/1', follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)
        self.assertIn(b'adicionado ao seu carrinho', res_add.data)

        # Apply coupon PRIMEIRACOMPRA (20%)
        res_coupon = self.client.post('/cart/apply-coupon', data={
            'coupon_code': 'PRIMEIRACOMPRA'
        }, follow_redirects=True)
        self.assertEqual(res_coupon.status_code, 200)
        self.assertIn(b'Desconto de 20%', res_coupon.data)

    def test_05_checkout_and_order(self):
        # Login with demo user
        self.client.post('/login', data={
            'email': 'gamer@teste.com',
            'password': '123456'
        })

        # Add product 2 to cart
        self.client.get('/cart/add/2')

        # Checkout POST
        res_checkout = self.client.post('/checkout', data={
            'name': 'Felipe Gamer',
            'email': 'gamer@teste.com',
            'payment_method': 'PIX'
        }, follow_redirects=True)
        self.assertEqual(res_checkout.status_code, 200)
        self.assertIn(b'LIBERADOS', res_checkout.data)
        self.assertIn(b'APEX-', res_checkout.data)

    def test_06_download_file(self):
        # Login first
        self.client.post('/login', data={
            'email': 'gamer@teste.com',
            'password': '123456'
        })
        res = self.client.get('/download/ultra_fps_pack.zip')
        self.assertEqual(res.status_code, 200)
        self.assertIn(res.headers.get('Content-Type'), ['application/zip', 'application/x-zip-compressed'])

    def test_07_admin_dashboard(self):
        # Login as admin
        self.client.post('/login', data={
            'email': 'admin@apexboost.com',
            'password': 'admin123'
        })
        res_admin = self.client.get('/admin')
        self.assertEqual(res_admin.status_code, 200)
        self.assertIn(b'ADMIN DASHBOARD', res_admin.data)
        self.assertIn(b'FATURAMENTO TOTAL', res_admin.data)

    def test_08_clear_orders(self):
        # Test clear orders endpoint
        self.client.post('/login', data={
            'email': 'admin@apexboost.com',
            'password': 'admin123'
        })
        res_clear = self.client.post('/admin/clear-orders', follow_redirects=True)
        self.assertEqual(res_clear.status_code, 200)
        self.assertIn(b'R$ 0,00', res_clear.data)
        self.assertIn(b'Nenhum pedido efetuado ainda', res_clear.data)

    def test_09_security_firewall_blocks_sensitive_files(self):
        # 1. Direct access to database file must be blocked (403)
        res_db = self.client.get('/store.db')
        self.assertEqual(res_db.status_code, 403)

        # 2. Direct access to .env must be blocked (403)
        res_env = self.client.get('/.env')
        self.assertEqual(res_env.status_code, 403)

        # 3. Direct access to zip files inside /static/downloads/ must be blocked (403)
        res_zip = self.client.get('/static/downloads/ultra_fps_pack.zip')
        self.assertEqual(res_zip.status_code, 403)

        # 4. Directory traversal tricks must be blocked (400 or 403)
        res_traversal = self.client.get('/static/../app.py')
        self.assertIn(res_traversal.status_code, [400, 403])

    def test_10_security_unauthorized_download_blocked(self):
        # Log in with user who hasn't purchased ultimate_extreme_suite.zip
        self.client.post('/login', data={
            'email': 'gamer@teste.com',
            'password': '123456'
        })
        res_unbought = self.client.get('/download/ultimate_extreme_suite.zip', follow_redirects=False)
        self.assertEqual(res_unbought.status_code, 302)
        self.assertIn('/#tab-packs', res_unbought.headers.get('Location', ''))

    def test_11_security_idor_order_protection(self):
        # Admin creates or gets an order
        conn = get_db()
        admin_order = conn.execute("SELECT order_code FROM orders WHERE user_id = 1").fetchone()
        conn.close()

        if admin_order:
            order_code = admin_order['order_code']
            # Log in as non-admin regular user
            self.client.post('/login', data={
                'email': 'gamer@teste.com',
                'password': '123456'
            })
            # Attempt to view admin's order receipt
            res_idor = self.client.get(f'/order/{order_code}', follow_redirects=False)
            self.assertEqual(res_idor.status_code, 302)
            self.assertEqual(res_idor.headers.get('Location'), '/')

    def test_12_security_headers_and_anti_cache(self):
        # Login
        self.client.post('/login', data={
            'email': 'gamer@teste.com',
            'password': '123456'
        })
        res = self.client.get('/cart')
        self.assertEqual(res.status_code, 200)

        # Verify HTTP security headers
        self.assertEqual(res.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(res.headers.get('X-Frame-Options'), 'SAMEORIGIN')
        self.assertEqual(res.headers.get('X-XSS-Protection'), '1; mode=block')
        self.assertEqual(res.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')
        self.assertIn("default-src 'self'", res.headers.get('Content-Security-Policy', ''))
        self.assertIn('no-store', res.headers.get('Cache-Control', ''))

    def test_13_security_open_redirect_prevented(self):
        # Attempt to exploit open redirect with external URL
        res = self.client.post('/login?next=//malicious-phishing.com', data={
            'email': 'gamer@teste.com',
            'password': '123456'
        }, follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        # Should NOT redirect to external malicious URL
        self.assertNotIn('malicious-phishing.com', res.headers.get('Location', ''))
        self.assertEqual(res.headers.get('Location'), '/')

if __name__ == '__main__':
    unittest.main()
