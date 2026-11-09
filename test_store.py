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

    def test_01_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'APEX', response.data)
        self.assertIn(b'BOOST', response.data)
        self.assertIn(b'Competitive FPS Ultra Pack', response.data)

    def test_02_product_detail(self):
        response = self.client.get('/pack/ultra-fps-competitive-pack')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Competitive FPS Ultra Pack', response.data)

    def test_03_registration_and_login(self):
        # Register new gamer
        test_email = "testgamer@domain.com"
        # Cleanup if exists
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

        # Logout
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)

        # Login
        res_login = self.client.post('/login', data={
            'email': test_email,
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Login realizado com sucesso', res_login.data)

    def test_04_cart_and_coupon(self):
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
        self.assertIn(b'APEX-', res_checkout.data) # License key

    def test_06_download_file(self):
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

if __name__ == '__main__':
    unittest.main()
