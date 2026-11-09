import sqlite3
import os
import json
import uuid
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'store.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        avatar TEXT DEFAULT 'gamer_avatar.png',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        tag TEXT,
        short_desc TEXT,
        description TEXT,
        price REAL NOT NULL,
        old_price REAL,
        badge TEXT,
        fps_gain TEXT,
        latency_drop TEXT,
        features TEXT, -- JSON string
        download_file TEXT,
        icon TEXT,
        popular INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_code TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        customer_name TEXT,
        customer_email TEXT,
        total REAL NOT NULL,
        discount REAL DEFAULT 0.0,
        coupon_used TEXT,
        payment_method TEXT NOT NULL,
        status TEXT DEFAULT 'PAGO',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        license_key TEXT NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    );

    CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        discount_percent INTEGER NOT NULL,
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT NOT NULL,
        game TEXT NOT NULL,
        rating INTEGER NOT NULL,
        text TEXT NOT NULL,
        fps_before INTEGER,
        fps_after INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Seed Default Admin & Demo User
    admin = cursor.execute("SELECT id FROM users WHERE email = ?", ('admin@apexboost.com',)).fetchone()
    if not admin:
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, is_admin)
            VALUES (?, ?, ?, 1)
        ''', ('Administrador Apex', 'admin@apexboost.com', generate_password_hash('admin123')))

    demo_user = cursor.execute("SELECT id FROM users WHERE email = ?", ('gamer@teste.com',)).fetchone()
    if not demo_user:
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, is_admin)
            VALUES (?, ?, ?, 0)
        ''', ('Felipe Gamer', 'gamer@teste.com', generate_password_hash('123456')))

    # Seed Coupons
    coupons = [
        ('FPSBOOST', 15),
        ('PRIMEIRACOMPRA', 20),
        ('VORTEX10', 10),
        ('CYBER25', 25)
    ]
    for code, disc in coupons:
        cursor.execute('''
            INSERT OR IGNORE INTO coupons (code, discount_percent)
            VALUES (?, ?)
        ''', (code, disc))

    # Seed Products
    default_products = [
        {
            "slug": "starter-tweak-pack",
            "name": "Starter Tweak Pack",
            "tag": "Iniciante & PCs Fracos",
            "short_desc": "Painel 1-Clique, limpeza profunda de cache, desativação de telemetria, alívio de RAM e plano Ultimate Performance.",
            "description": "O Starter Tweak Pack é a porta de entrada para quem quer reviver um PC lento ou extrair os primeiros 20-30 FPS a mais. Remove com segurança aplicativos desnecessários do Windows, desativa telemetria que consome CPU em segundo plano, limpa caches do sistema, libera memória RAM em espera e ativa o modo de Desempenho Máximo.",
            "price": 9.90,
            "old_price": 24.90,
            "badge": "MAIS ECONÔMICO",
            "fps_gain": "+25% FPS",
            "latency_drop": "-15ms Delay",
            "features": json.dumps([
                "Painel Master com Execução Total em 1 Clique",
                "Limpeza Profunda de Temp, Cache e Prefetch",
                "Liberador Ativo de Memória RAM Ociosa (Standby Cache)",
                "Desativação de Telemetria e Diagnósticos da Microsoft",
                "Desativação do Xbox Game Bar DVR em Segundo Plano",
                "Desativação de Notificações, Anúncios e Animações",
                "Ativação do Plano 'Apex Ultimate Performance'",
                "Mouse Raw Input 1:1 Sem Aceleração Nociva",
                "Ponto de Restauração & Undo 100% Seguro",
                "Guia Passo a Passo em Português"
            ]),
            "download_file": "starter_pack.zip",
            "icon": "bi-lightning-charge",
            "popular": 0
        },
        {
            "slug": "ultra-fps-competitive-pack",
            "name": "Competitive FPS Ultra Pack",
            "tag": "Mais Vendido para Competitivo",
            "short_desc": "Otimização profunda de GPU (Nvidia/AMD), CPU Core Unparking, redução brutal de input lag e estabilização de 1% Low.",
            "description": "Desenvolvido especificamente para jogadores de Valorant, CS2, Fortnite, Warzone e FiveM. O Competitive Ultra Pack reconfigura os timers de alta precisão do Windows (HPET / Synthetic Timers), unpark dos núcleos do processador, perfil avançado de driver de vídeo com DPC Latency minimizado e prioridade exclusiva para o processo do seu jogo.",
            "price": 19.90,
            "old_price": 49.90,
            "badge": "MAIS VENDIDO ⭐",
            "fps_gain": "+60% FPS",
            "latency_drop": "-35ms Delay",
            "features": json.dumps([
                "Tudo do Starter Pack Incluso (20+ Ferramentas)",
                "CPU Core Unparking (100% dos Núcleos Destravados)",
                "Ajuste Fino de Timer Resolution para 0.5ms Estável",
                "Desativação de HPET (Elimina Gargalos de Clock)",
                "Ativação de HAGS (Agendamento de GPU Acelerado)",
                "Modo de Jogo Nativo + Prioridade High para Jogos",
                "Desativação de Otimizações de Tela Inteira (FSE Fix)",
                "Buffer de Teclado Ultra-Responsivo sem Repetição Lenta",
                "Otimização de SSD com Comando TRIM Forçado",
                "Guia Competitivo Exclusivo para CS2, Valorant e Warzone",
                "Total Compatibilidade com Windows 10 e 11"
            ]),
            "download_file": "ultra_fps_pack.zip",
            "icon": "bi-fire",
            "popular": 1
        },
        {
            "slug": "zero-latency-network-streamer",
            "name": "Zero Latency & Network Pro",
            "tag": "Ping Baixo & Alta Taxa de Quadros",
            "short_desc": "Otimização extrema da pilha de rede TCP/IP, redução de jitter, MTU customizado e priorização para streaming sem perda de frames.",
            "description": "Se você sofre com oscilação de ping, perda de pacotes (packet loss) ou quer streamar no OBS sem derrubar o FPS do jogo, este pack é indispensável. Otimiza buffers de placa de rede, desativa algoritmos de Nagle (TcpAckFrequency), define DNS de ultra baixa latência e otimiza a codificação NVENC/AMF.",
            "price": 24.90,
            "old_price": 59.90,
            "badge": "ZERO LAG REDE",
            "fps_gain": "+45% FPS",
            "latency_drop": "-45ms Delay / -18ms Ping",
            "features": json.dumps([
                "Tudo do Starter Pack Incluso",
                "Otimização TCP/IP e Pilha Window Auto-Tuning",
                "Desativação do Algoritmo de Nagle (TcpAckFrequency = 1)",
                "Eliminação de Packet Loss e Variação de Jitter",
                "Configurador Automático de DNS Gamer Cloudflare & Google",
                "Priorização de Pacotes UDP para Jogos Online",
                "Presets Otimizados para OBS Studio / Streamlabs",
                "Desativação de Limitações de Rede (Network Throttling)",
                "Scripts Automáticos com Backup e Reversão"
            ]),
            "download_file": "network_pro_pack.zip",
            "icon": "bi-broadcast-pin",
            "popular": 0
        },
        {
            "slug": "ultimate-extreme-suite",
            "name": "Ultimate Extreme Suite (All-In-One)",
            "tag": "O Pack Definitivo de Otimização",
            "short_desc": "Painel Master Apex Optimizer Pro com menus interativos: escolha e execute tweaks por categoria ou em 1 clique total.",
            "description": "O ápice em desempenho para PC Gamer. Inclui o exclusivo painel Apex Optimizer Master Pro (v3.5) com submenus interativos para você escolher e executar exatamente o que deseja: Limpeza de RAM/Caches, CPU Core Unparking, Timers a 0.5ms, HAGS, Modo de Jogo, Zero Input Lag, Desativação do Nagle/DNS Gamer e Bloatware Off, além de opção de Reversão Total.",
            "price": 34.90,
            "old_price": 79.90,
            "badge": "VITALÍCIO & VIP 👑",
            "fps_gain": "+85% FPS",
            "latency_drop": "-55ms Delay / 0ms Latency",
            "features": json.dumps([
                "Apex Optimizer Master Pro v3.5 com Menus Interativos",
                "Opções Individuais para Escolher e Executar Tweaks",
                "Otimização Total em 1 Clique com Barra de Progresso",
                "CPU Core Unparking + Timer Resolution 0.5ms + HPET Off",
                "GPU Tuning: HAGS, DWM Low Latency & HighPriority",
                "Zero Input Lag: Raw Input 1:1 e Buffer Instantâneo",
                "Rede Gamer: Nagle Disable, MTU Tuning e DNS 1.1.1.1",
                "Limpeza Profunda de RAM (Standby Cache) e SSD TRIM",
                "Guia Completo de BIOS: XMP/EXPO, ReBAR e C-States",
                "Chave de Ativação VIP com Atualizações Vitalícias",
                "Backup do Registro + Ponto de Restauração + Undo Total"
            ]),
            "download_file": "ultimate_extreme_suite.zip",
            "icon": "bi-gem",
            "popular": 0
        }
    ]

    for prod in default_products:
        existing = cursor.execute("SELECT id FROM products WHERE slug = ?", (prod['slug'],)).fetchone()
        if not existing:
            cursor.execute('''
                INSERT INTO products (
                    slug, name, tag, short_desc, description, price, old_price,
                    badge, fps_gain, latency_drop, features, download_file, icon, popular
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prod['slug'], prod['name'], prod['tag'], prod['short_desc'], prod['description'],
                prod['price'], prod['old_price'], prod['badge'], prod['fps_gain'], prod['latency_drop'],
                prod['features'], prod['download_file'], prod['icon'], prod['popular']
            ))
        else:
            cursor.execute('''
                UPDATE products SET
                    name = ?, tag = ?, short_desc = ?, description = ?,
                    price = ?, old_price = ?, badge = ?, fps_gain = ?, latency_drop = ?,
                    features = ?, download_file = ?, icon = ?, popular = ?
                WHERE slug = ?
            ''', (
                prod['name'], prod['tag'], prod['short_desc'], prod['description'],
                prod['price'], prod['old_price'], prod['badge'], prod['fps_gain'], prod['latency_drop'],
                prod['features'], prod['download_file'], prod['icon'], prod['popular'],
                prod['slug']
            ))

    # Seed Reviews
    reviews_count = cursor.execute("SELECT COUNT(*) as cnt FROM reviews").fetchone()['cnt']
    if reviews_count == 0:
        default_reviews = [
            ("Gabriel 'coldzera' S.", "CS2", 5, "Mano, meu CS2 saía de 140 FPS e dropava pra 70 nas smokes. Depois de aplicar o Competitive Ultra Pack, travou em 230 FPS e os stutters sumiram completamente! Valeu cada centavo.", 140, 230),
            ("Lucas 'Nox' Ferreira", "Valorant", 5, "O input lag do mouse mudou da água pro vinho. Parece que a mira tá grudando no alvo de tão liso. E a entrega foi instantânea via PIX!", 180, 290),
            ("Matheus 'Kzinn' Ribeiro", "Warzone", 5, "Warzone sempre foi um pesadelo no meu PC (GTX 1660 Ti). Com a Ultimate Suite ganhei mais de 45 FPS e o jogo não engasga mais quando cai do avião.", 65, 112),
            ("Rafael 'FaZeBR' Lima", "Fortnite", 5, "Peguei o Pack Extreme e me surpreendi. Os scripts .bat são super organizados, criam ponto de restauração antes de mexer e deixam o Windows voando. Top demais!", 120, 210),
            ("Vinicius 'StreamerV' Costa", "OBS + FiveM", 5, "O pack de rede e latência salvou minhas lives. O FiveM antes dropava frame toda hora por causa do streaming. Agora roda limpo a 144hz.", 90, 155)
        ]
        for author, game, rating, text, before, after in default_reviews:
            cursor.execute('''
                INSERT INTO reviews (author, game, rating, text, fps_before, fps_after)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (author, game, rating, text, before, after))

    conn.commit()
    conn.close()

def generate_license_key():
    parts = [uuid.uuid4().hex[:4].upper() for _ in range(4)]
    return f"APEX-{'-'.join(parts)}"

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")

