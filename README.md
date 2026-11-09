# ⚡ Apex Boost Labs - Loja Completa de Packs de Otimização para PC

Uma plataforma moderna e completa de e-commerce gamer voltada para a venda e distribuição de **Packs de Otimização de FPS, Redução de Input Lag e Debloat para Windows 10/11**.

---

## 🎮 Principais Funcionalidades

### 1. Sistema de Autenticação Completo
- **Cadastro de Usuários**: Validação de campos, senha mínima, confirmação e hash criptográfico seguro (`Werkzeug`).
- **Login e Sessão**: Sessão com cookies protegidos, redirecionamento inteligente pós-login.
- **Painel do Membro (`/profile`)**:
  - **Central de Downloads e Licenças**: Acesso vitalício a todos os packs comprados com suas respectivas chaves de licença únicas (`APEX-XXXX-XXXX-XXXX-XXXX`).
  - **Histórico de Pedidos**: Detalhamento de compras, método de pagamento, data e status.
  - **Configurações da Conta**: Atualização de nome e troca de senha.

### 2. Loja e Experiência Gamer
- **Simulador Interativo de FPS**: Calcule em tempo real o ganho de FPS e queda de latência escolhendo o jogo (*Valorant, CS2, Fortnite, Warzone, FiveM, Apex*), o hardware do PC e o pack.
- **Catálogo de Packs**:
  1. *Starter Tweak Pack* (Iniciante & PCs Fracos - R$ 19,90)
  2. *Competitive FPS Ultra Pack* (Mais Vendido ⭐ - R$ 39,90)
  3. *Zero Latency & Network Pro* (Rede & OBS - R$ 49,90)
  4. *Ultimate Extreme Suite* (All-In-One Definitivo & VIP - R$ 69,90)
- **Páginas de Detalhes dos Produtos**: Lista completa de scripts, requisitos e garantia.
- **Depoimentos e Benchmarks**: Prova social com reviews de jogadores reais e comparativos antes vs depois.
- **Notificações Flutuantes (Social Proof)**: Alertas em tempo real de compras recentes ("Matheus acabou de adquirir o Pack Ultra").

### 3. Carrinho e Checkout Express
- **Carrinho Dinâmico**: Adição via AJAX sem recarregar a página, contador no navbar.
- **Sistema de Cupons de Desconto**:
  - `PRIMEIRACOMPRA` (20% OFF)
  - `FPSBOOST` (15% OFF)
  - `CYBER25` (25% OFF)
- **Checkout com Pagamento Simulado**:
  - **PIX Instantâneo**: QR Code dinâmico e chave Copia e Cola funcional.
  - **Cartão de Crédito**: Validação de campos e parcelamento até 12x.
- **Entrega Imediata**: Geração automática de chave de licença e liberação do download do arquivo `.zip`.

### 4. Packs Reais para Download
Cada pack conta com arquivos reais e seguros (`.bat`, `.reg`, tutoriais):
- Ponto de Restauração automático do Windows
- Limpeza profunda de temporários, Prefetch e cache DNS
- Desativação de telemetria e diagnósticos ocultos
- Ativação do Plano de Desempenho Máximo (Ultimate Performance)
- Desbloqueio de núcleos de CPU (Core Unparking)
- Timer Resolution de ultra baixa latência (0.5ms)
- Otimizações de registro e rede TCP/IP sem risco de ban

### 5. Painel Administrativo (`/admin`)
- Métrica de Faturamento Total, Pedidos, Usuários e Packs
- Tabela com histórico completo de vendas
- Gerenciador de status dos produtos (Ativar / Ocultar)
- Criador de novos cupons de desconto
- Visualização de todos os clientes registrados

---

## 🔑 Contas Pré-Configuradas



*Você também pode criar quantas contas novas desejar pela página de cadastro.*

---

## 🚀 Como Iniciar a Loja

### Opção 1: Pelo executável rápido
Dê um duplo clique no arquivo:
```cmd
iniciar_loja.bat
```

### Opção 2: Pelo terminal
```bash
py app.py
```
Acesse no seu navegador: **`http://127.0.0.1:5000`**

---

## 🧪 Como Rodar os Testes Automatizados
```bash
py test_store.py
```
Todos os 7 testes validam fluxo de compras, banco de dados, downloads e autenticação.

