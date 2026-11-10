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

    def test_14_drop_vip_single_claim(self):
        # 1. Unauthenticated request to /api/claim-drop returns 401
        res_unauth = self.client.post('/api/claim-drop')
        self.assertEqual(res_unauth.status_code, 401)

        # 2. Register fresh user for Drop VIP test
        drop_user_email = "newuser_drop@test.com"
        conn = get_db()
        conn.execute("DELETE FROM users WHERE email = ?", (drop_user_email,))
        conn.commit()
        conn.close()

        self.client.post('/register', data={
            'name': 'Novo Gamer Drop',
            'email': drop_user_email,
            'password': 'password123',
            'confirm_password': 'password123'
        })

        # 3. First claim should succeed and apply coupon
        res_claim1 = self.client.post('/api/claim-drop')
        self.assertEqual(res_claim1.status_code, 200)
        data1 = json.loads(res_claim1.data)
        self.assertTrue(data1['success'])
        self.assertEqual(data1['coupon'], 'PRIMEIRACOMPRA')
        self.assertEqual(data1['discount'], 20)

        # 4. Second claim by the SAME user must be REJECTED (already claimed)
        res_claim2 = self.client.post('/api/claim-drop')
        self.assertEqual(res_claim2.status_code, 400)
        data2 = json.loads(res_claim2.data)
        self.assertFalse(data2['success'])
        self.assertTrue(data2['already_claimed'])

        # 5. Status endpoint should report claimed: True
        res_status = self.client.get('/api/drop-status')
        self.assertEqual(res_status.status_code, 200)
        data_status = json.loads(res_status.data)
        self.assertTrue(data_status['claimed'])

    def test_15_ajax_login_animation_support(self):
        """Testa o suporte AJAX do endpoint de login para as animações de carregamento e autenticação"""
        # 1. Missing credentials returns 400
        res_empty = self.client.post('/login', headers={'X-Requested-With': 'XMLHttpRequest'}, data={})
        self.assertEqual(res_empty.status_code, 400)
        data_empty = json.loads(res_empty.data)
        self.assertFalse(data_empty['success'])

        # 2. Invalid credentials returns 401
        res_invalid = self.client.post('/login', headers={'X-Requested-With': 'XMLHttpRequest'}, data={
            'email': 'inexistente@apex.com',
            'password': 'errada'
        })
        self.assertEqual(res_invalid.status_code, 401)
        data_invalid = json.loads(res_invalid.data)
        self.assertFalse(data_invalid['success'])
        self.assertIn('incorretos', data_invalid['message'])

        # 3. Valid credentials returns 200 with JSON redirect_url
        res_valid = self.client.post('/login', headers={'X-Requested-With': 'XMLHttpRequest'}, data={
            'email': 'admin@apexboost.com',
            'password': 'admin123'
        })
        self.assertEqual(res_valid.status_code, 200)
        data_valid = json.loads(res_valid.data)
        self.assertTrue(data_valid['success'])
        self.assertTrue(data_valid['redirect_url'])

    def test_16_anti_leak_password_policy(self):
        """Verifica bloqueio de senhas que constam em vazamentos conhecidos"""
        # 1. Tentar cadastrar com senha vazada comum '123456' deve ser bloqueado
        res_weak = self.client.post('/register', headers={'X-Requested-With': 'XMLHttpRequest'}, data={
            'name': 'Hacker Tester',
            'email': 'hacker@teste.com',
            'password': '123456',
            'confirm_password': '123456'
        })
        self.assertEqual(res_weak.status_code, 400)
        data_weak = json.loads(res_weak.data)
        self.assertFalse(data_weak['success'])
        self.assertIn('vazamentos', data_weak['message'].lower())

    def test_17_admin_product_and_coupon_management(self):
        """Testa o cadastro de novos produtos, gerenciamento de cupons e alternância de status de pedidos no painel admin"""
        # 1. Login as admin
        self.client.post('/login', data={
            'email': 'admin@apexboost.com',
            'password': 'admin123'
        })

        # 2. Add a new product
        res_add_prod = self.client.post('/admin/add-product', data={
            'name': 'Otimização Remota VIP AnyDesk',
            'price': '79.90',
            'old_price': '149.90',
            'tag': 'Atendimento 1-a-1',
            'badge': 'VIP 👑',
            'fps_gain': '+95% FPS',
            'latency_drop': '-60ms Delay',
            'short_desc': 'Ajuste feito por especialista via AnyDesk',
            'features': "Atendimento individual\nAjuste de BIOS\nRedução de Input Lag",
            'download_file': 'ultra_fps_pack.zip',
            'icon': 'bi-headset'
        }, follow_redirects=True)
        self.assertEqual(res_add_prod.status_code, 200)
        self.assertIn(b'cadastrado com sucesso', res_add_prod.data)
        self.assertIn(b'Otimiza', res_add_prod.data)

        # 3. Add and delete coupon
        res_add_c = self.client.post('/admin/add-coupon', data={
            'code': 'TESTEADMIN30',
            'discount': '30'
        }, follow_redirects=True)
        self.assertEqual(res_add_c.status_code, 200)
        self.assertIn(b'TESTEADMIN30', res_add_c.data)

    def test_18_dual_admin_and_client_sessions(self):
        """Testa o isolamento de sessões simultâneas entre a aba do Administrador e a aba do Cliente no mesmo navegador"""
        # 1. Login inicial como Administrador (Aba 1)
        res_admin_login = self.client.post('/login', data={
            'email': 'admin@apexboost.com',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(res_admin_login.status_code, 200)

        # 2. Verifica que o Admin acessa o painel normalmente
        res_dash = self.client.get('/admin')
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn(b'ADMIN DASHBOARD', res_dash.data)

        # 3. Na mesma sessão do navegador (simulando a Aba 2), loga como cliente comum
        res_client_login = self.client.post('/login', data={
            'email': 'gamer@teste.com',
            'password': '123456'
        }, follow_redirects=True)
        self.assertEqual(res_client_login.status_code, 200)
        self.assertIn(b'Felipe Gamer', res_client_login.data)

        # 4. Verifica que a Aba 2 (Cliente) está autenticada com os dados do cliente
        res_profile = self.client.get('/profile')
        self.assertEqual(res_profile.status_code, 200)
        self.assertIn(b'Felipe Gamer', res_profile.data)

        # 5. CRÍTICO: Volta para a Aba 1 (Admin) e dá refresh no /admin
        # Não deve tomar 403 nem ser redirecionado para a vitrine!
        res_admin_tab = self.client.get('/admin')
        self.assertEqual(res_admin_tab.status_code, 200)
        self.assertIn(b'ADMIN DASHBOARD', res_admin_tab.data)

        # 6. Admin consegue executar ações administrativas sem interferência
        res_action = self.client.post('/admin/add-coupon', data={
            'code': 'DUALSESSION20',
            'discount': '20'
        }, follow_redirects=True)
        self.assertEqual(res_action.status_code, 200)
        self.assertIn(b'DUALSESSION20', res_action.data)

        # 7. Cliente na Aba 2 clica em "Sair" (/logout)
        res_client_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_client_logout.status_code, 200)

        # 8. O painel admin /admin CONTINUA autenticado e acessível!
        res_admin_still_ok = self.client.get('/admin')
        self.assertEqual(res_admin_still_ok.status_code, 200)
        self.assertIn(b'ADMIN DASHBOARD', res_admin_still_ok.data)

        # 9. Quando o Admin explicitamente faz logout pelo /admin/logout
        res_admin_logout = self.client.get('/admin/logout', follow_redirects=True)
        self.assertEqual(res_admin_logout.status_code, 200)

        # 10. Agora o acesso a /admin é devidamente bloqueado
        res_admin_blocked = self.client.get('/admin')
        self.assertEqual(res_admin_blocked.status_code, 302)

if __name__ == '__main__':
    unittest.main()
