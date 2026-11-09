// Apex Boost Labs - Frontend Interactivity & Gaming Experience

// ==========================================================================
// Web Audio API Gamer Sound Engine (Synthesizer based - no external assets)
// ==========================================================================
const ApexSound = (function() {
    let audioCtx = null;
    let enabled = localStorage.getItem('apex_sound_enabled') !== 'false';

    function getContext() {
        if (!audioCtx && (window.AudioContext || window.webkitAudioContext)) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx && audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        return audioCtx;
    }

    function isEnabled() {
        return enabled;
    }

    function toggle() {
        enabled = !enabled;
        localStorage.setItem('apex_sound_enabled', enabled ? 'true' : 'false');
        updateSoundIcons(enabled);
        if (enabled) {
            playTone(880, 0.08, 'sine', 0.05);
        }
        return enabled;
    }

    function updateSoundIcons(isOn) {
        document.querySelectorAll('.sound-icon').forEach(icon => {
            icon.className = isOn ? 'bi bi-volume-up-fill sound-icon text-cyan' : 'bi bi-volume-mute-fill sound-icon text-secondary';
        });
        document.querySelectorAll('.sound-label').forEach(label => {
            label.textContent = isOn ? 'Som: On' : 'Som: Mudo';
        });
    }

    function playTone(freq, duration, type = 'sine', gainVal = 0.035) {
        if (!enabled) return;
        try {
            const ctx = getContext();
            if (!ctx) return;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, ctx.currentTime);
            gain.gain.setValueAtTime(gainVal, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + duration);
        } catch(e) {}
    }

    function playClick() {
        playTone(720, 0.035, 'triangle', 0.025);
    }

    function playSuccess() {
        if (!enabled) return;
        try {
            const ctx = getContext();
            if (!ctx) return;
            const now = ctx.currentTime;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(523.25, now);
            osc.frequency.setValueAtTime(783.99, now + 0.07);
            gain.gain.setValueAtTime(0.05, now);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.22);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(now);
            osc.stop(now + 0.22);
        } catch(e) {}
    }

    return {
        toggle,
        isEnabled,
        playClick,
        playSuccess,
        updateSoundIcons
    };
})();

// ==========================================================================
// Initialization on DOM Ready
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initSoundToggle();
    initSidebarTabs();
    initTelemetryComparator();
    initPackSearchAndFilters();
    initBottleneckScanner();
    initMysteryDropModal();
    initLiveSalesToast();
    initFpsCalculator();
    initAjaxAddToCart();
    initCopyButtons();
    initPixTimer();
    initCheckoutEnhancements();
    initGlobalSoundEffects();
});

// Sound Toggle Handler
function initSoundToggle() {
    ApexSound.updateSoundIcons(ApexSound.isEnabled());
    document.querySelectorAll('.sound-toggle-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            ApexSound.toggle();
        });
    });
}

// Global UI Sounds on interactive buttons
function initGlobalSoundEffects() {
    document.querySelectorAll('.sidebar-nav-item, .btn-apex-outline, .filter-pill, .mode-switch-btn, .sidebar-quick-btn, .btn-sidebar-action').forEach(btn => {
        btn.addEventListener('click', () => {
            ApexSound.playClick();
        });
    });
}

// ==========================================================================
// Theme Toggle (Light Off-White / Dark Obsidian with Electric Cobalt)
// ==========================================================================
function initThemeToggle() {
    const toggleBtns = document.querySelectorAll('.theme-toggle-btn');
    const icons = document.querySelectorAll('.theme-icon');
    const labels = document.querySelectorAll('.theme-label');

    function updateIcons(isDark) {
        icons.forEach(icon => {
            if (isDark) {
                icon.className = 'bi bi-sun-fill text-warning theme-icon';
            } else {
                icon.className = 'bi bi-moon-stars-fill theme-icon';
            }
        });
        labels.forEach(label => {
            label.textContent = isDark ? 'Escuro' : 'Claro';
        });
    }

    function applyTheme(isDark) {
        if (isDark) {
            document.body.classList.add('theme-dark');
            document.documentElement.classList.add('theme-dark');
            document.body.setAttribute('data-bs-theme', 'dark');
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            localStorage.setItem('apex_theme', 'dark');
        } else {
            document.body.classList.remove('theme-dark');
            document.documentElement.classList.remove('theme-dark');
            document.body.setAttribute('data-bs-theme', 'light');
            document.documentElement.setAttribute('data-bs-theme', 'light');
            localStorage.setItem('apex_theme', 'light');
        }
        updateIcons(isDark);
    }

    const currentTheme = localStorage.getItem('apex_theme') || 'light';
    applyTheme(currentTheme === 'dark');

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const willBeDark = !document.body.classList.contains('theme-dark');
            applyTheme(willBeDark);
            ApexSound.playClick();
        });
    });
}

// ==========================================================================
// Dynamic Sidebar Tab Switching (Zero page jumping - SPA feel)
// ==========================================================================
function initSidebarTabs() {
    const tabTriggers = document.querySelectorAll('[data-tab-target]');
    const tabPanes = document.querySelectorAll('.store-tab-pane');
    const sidebarNavItems = document.querySelectorAll('.sidebar-nav-item[data-tab-target]');

    function activateTab(tabId) {
        if (!tabId) tabId = 'tab-home';
        if (!tabId.startsWith('tab-')) {
            tabId = 'tab-' + tabId;
        }

        if (tabPanes.length > 0) {
            let found = false;
            tabPanes.forEach(pane => {
                if (pane.id === tabId) {
                    pane.classList.add('active');
                    found = true;
                } else {
                    pane.classList.remove('active');
                }
            });

            if (!found && tabPanes[0]) {
                tabPanes[0].classList.add('active');
                tabId = tabPanes[0].id;
            }

            // Update active state in sidebar
            sidebarNavItems.forEach(item => {
                const target = item.getAttribute('data-tab-target');
                if (target === tabId || ('tab-' + target) === tabId) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });

            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    tabTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            const targetId = this.getAttribute('data-tab-target');
            if (tabPanes.length > 0) {
                e.preventDefault();
                activateTab(targetId);
                try {
                    window.history.pushState(null, '', '#' + targetId);
                } catch(err) {}

                // Close mobile sidebar if open
                const sidebar = document.getElementById('appSidebar');
                const overlay = document.getElementById('mobileSidebarOverlay');
                if (sidebar) sidebar.classList.remove('show');
                if (overlay) overlay.classList.remove('show');
            }
        });
    });

    if (tabPanes.length > 0) {
        const hash = window.location.hash.replace('#', '');
        if (hash) {
            activateTab(hash);
        } else {
            activateTab('tab-home');
        }
    }
}

// ==========================================================================
// Interactive Before / After Telemetry Comparator
// ==========================================================================
function initTelemetryComparator() {
    const btnStandard = document.getElementById('btnModeStandard');
    const btnOptimized = document.getElementById('btnModeOptimized');

    if (!btnStandard || !btnOptimized) return;

    const val1Low = document.getElementById('val1PercentLow');
    const bar1Low = document.getElementById('bar1PercentLow');
    const valInput = document.getElementById('valInputLag');
    const barInput = document.getElementById('barInputLag');
    const valTimer = document.getElementById('valTimerRes');
    const barTimer = document.getElementById('barTimerRes');
    const valProc = document.getElementById('valProcesses');
    const barProc = document.getElementById('barProcesses');

    const statusEl = document.getElementById('boxCompareStatus');
    const mainMetricEl = document.getElementById('boxCompareMainMetric');
    const descEl = document.getElementById('boxCompareDesc');
    const metricSmoothEl = document.getElementById('metricSmooth');
    const metricDpcEl = document.getElementById('metricDpc');
    const metricRamEl = document.getElementById('metricRam');

    function setStandardMode() {
        btnStandard.classList.add('active');
        btnOptimized.classList.remove('active');

        if (val1Low) { val1Low.textContent = '48 FPS (Quedas Bruscas)'; val1Low.className = 'fw-black text-danger'; }
        if (bar1Low) { bar1Low.style.width = '25%'; bar1Low.className = 'metric-bar-fill bg-danger'; }

        if (valInput) { valInput.textContent = '16.8 ms (Atraso Alto)'; valInput.className = 'fw-black text-danger'; }
        if (barInput) { barInput.style.width = '85%'; barInput.className = 'metric-bar-fill bg-danger'; }

        if (valTimer) { valTimer.textContent = '15.6 ms (Desperdiçando Clock)'; valTimer.className = 'fw-black text-secondary'; }
        if (barTimer) { barTimer.style.width = '80%'; barTimer.className = 'metric-bar-fill bg-warning'; }

        if (valProc) { valProc.textContent = '192 Processos Ativos'; valProc.className = 'fw-black text-danger'; }
        if (barProc) { barProc.style.width = '90%'; barProc.className = 'metric-bar-fill bg-danger'; }

        if (statusEl) statusEl.textContent = 'Status: Computador com Configuração Padrão do Windows';
        if (mainMetricEl) { mainMetricEl.textContent = '115 FPS Médio'; mainMetricEl.style.color = '#ef4444'; }
        if (descEl) descEl.textContent = 'O processador tem núcleos adormecidos (Core Parking), o timer oscila em 15ms e serviços do Windows disputam ciclos com a sua GPU.';
        if (metricSmoothEl) { metricSmoothEl.textContent = 'Irregular'; metricSmoothEl.style.color = '#ef4444'; }
        if (metricDpcEl) { metricDpcEl.textContent = '850 µs'; metricDpcEl.className = 'fs-6 text-warning'; }
        if (metricRamEl) { metricRamEl.textContent = '3.2 GB'; }
    }

    function setOptimizedMode() {
        btnOptimized.classList.add('active');
        btnStandard.classList.remove('active');

        if (val1Low) { val1Low.textContent = '135 FPS (Cravado & Liso!)'; val1Low.className = 'fw-black text-success'; }
        if (bar1Low) { bar1Low.style.width = '95%'; bar1Low.className = 'metric-bar-fill bg-success'; }

        if (valInput) { valInput.textContent = '2.4 ms (Instantâneo ⚡)'; valInput.className = 'fw-black text-info'; }
        if (barInput) { barInput.style.width = '12%'; barInput.className = 'metric-bar-fill bg-info'; }

        if (valTimer) { valTimer.textContent = '0.500 ms (Precisão Máxima HPET)'; valTimer.className = 'fw-black text-primary'; }
        if (barTimer) { barTimer.style.width = '100%'; barTimer.className = 'metric-bar-fill bg-primary'; }

        if (valProc) { valProc.textContent = '68 Processos Enxutos'; valProc.className = 'fw-black text-success'; }
        if (barProc) { barProc.style.width = '28%'; barProc.className = 'metric-bar-fill bg-success'; }

        if (statusEl) statusEl.textContent = 'Status: Máquina Tunada com Apex Boost Master Pro';
        if (mainMetricEl) { mainMetricEl.textContent = '240+ FPS Estáveis'; mainMetricEl.style.color = '#00d2ff'; }
        if (descEl) descEl.textContent = 'Todos os núcleos destravados (Unpark CPU), latência de DPC abaixo de 50µs e fila de renderização prioritária para o jogo.';
        if (metricSmoothEl) { metricSmoothEl.textContent = 'Ultra Fluido 144/240Hz'; metricSmoothEl.style.color = '#10b981'; }
        if (metricDpcEl) { metricDpcEl.textContent = '38 µs'; metricDpcEl.className = 'fs-6 text-success'; }
        if (metricRamEl) { metricRamEl.textContent = '6.8 GB Livres'; }
    }

    btnStandard.addEventListener('click', () => {
        ApexSound.playClick();
        setStandardMode();
    });

    btnOptimized.addEventListener('click', () => {
        ApexSound.playSuccess();
        setOptimizedMode();
    });
}

// ==========================================================================
// Live Search & Category Filter Pills for Packs Catalog
// ==========================================================================
function initPackSearchAndFilters() {
    const searchInput = document.getElementById('packSearchInput');
    const filterPills = document.querySelectorAll('#packFilterPills .filter-pill');
    const packItems = document.querySelectorAll('.pack-item-col');
    const grid = document.getElementById('packsGrid');

    if (!packItems.length) return;

    let activeFilter = 'all';

    function applyFilterAndSearch() {
        const query = (searchInput?.value || '').trim().toLowerCase();
        let visibleCount = 0;

        packItems.forEach(item => {
            const name = item.getAttribute('data-name') || '';
            const desc = item.getAttribute('data-desc') || '';
            const tag = item.getAttribute('data-tag') || '';
            const isPopular = item.getAttribute('data-popular') === '1';
            const slug = item.getAttribute('data-slug') || '';

            // Pill category filter
            let passesFilter = true;
            if (activeFilter === 'cs2') {
                passesFilter = name.includes('fps') || name.includes('extreme') || desc.includes('cs2') || desc.includes('valorant');
            } else if (activeFilter === 'popular') {
                passesFilter = isPopular || slug === 'ultra_fps_pack';
            } else if (activeFilter === 'ping') {
                passesFilter = slug === 'network_pro_pack' || tag.includes('ping') || desc.includes('rede') || desc.includes('tcp');
            } else if (activeFilter === 'basic') {
                passesFilter = slug === 'starter_fps_pack' || desc.includes('básico') || desc.includes('pc fraco');
            }

            // Keyword text search
            let passesQuery = true;
            if (query.length > 0) {
                const combined = `${name} ${desc} ${tag}`.toLowerCase();
                passesQuery = combined.includes(query);
            }

            if (passesFilter && passesQuery) {
                item.style.display = '';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });

        // Placeholder if no items match
        let noResultsEl = document.getElementById('noPacksFoundMsg');
        if (visibleCount === 0) {
            if (!noResultsEl && grid) {
                noResultsEl = document.createElement('div');
                noResultsEl.id = 'noPacksFoundMsg';
                noResultsEl.className = 'col-12 text-center py-5 glass-card';
                noResultsEl.innerHTML = `
                    <i class="bi bi-search fs-1 text-blue mb-3 d-block"></i>
                    <h5 class="text-white fw-bold">Nenhum pacote encontrado para sua busca</h5>
                    <p class="text-secondary small mb-3">Tente buscar por "FPS", "Ping", "CS2", "RAM" ou limpe os filtros.</p>
                    <button type="button" class="btn btn-sm btn-apex-primary" id="btnClearPackFilter">
                        <i class="bi bi-arrow-counterclockwise me-1"></i> Ver Todos os Pacotes
                    </button>
                `;
                grid.appendChild(noResultsEl);
                document.getElementById('btnClearPackFilter')?.addEventListener('click', () => {
                    if (searchInput) searchInput.value = '';
                    activeFilter = 'all';
                    filterPills.forEach(p => p.classList.toggle('active', p.getAttribute('data-filter') === 'all'));
                    applyFilterAndSearch();
                });
            }
        } else if (noResultsEl) {
            noResultsEl.remove();
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            applyFilterAndSearch();
        });
    }

    filterPills.forEach(pill => {
        pill.addEventListener('click', function() {
            filterPills.forEach(p => p.classList.remove('active'));
            this.classList.add('active');
            activeFilter = this.getAttribute('data-filter') || 'all';
            ApexSound.playClick();
            applyFilterAndSearch();
        });
    });
}

// ==========================================================================
// Live Sales Toast (Social Proof)
// ==========================================================================
function initLiveSalesToast() {
    const toastEl = document.getElementById('liveSalesToast');
    if (!toastEl) return;

    let notifications = [];
    
    fetch('/api/live-sales')
        .then(res => res.json())
        .then(data => {
            notifications = data;
            startToastLoop();
        })
        .catch(() => {
            notifications = [
                { buyer: "Matheus S. (RJ)", pack: "Competitive FPS Ultra Pack", time: "há 2 min" },
                { buyer: "Lucas F. (SP)", pack: "Ultimate Extreme Suite", time: "há 5 min" },
                { buyer: "Pedro H. (MG)", pack: "Zero Latency & Network Pro", time: "há 9 min" }
            ];
            startToastLoop();
        });

    let index = 0;
    function showToast() {
        if (!notifications.length) return;
        const current = notifications[index % notifications.length];
        index++;

        const buyerEl = document.getElementById('toastBuyer');
        const packEl = document.getElementById('toastPack');
        const timeEl = document.getElementById('toastTime');

        if (buyerEl) buyerEl.textContent = current.buyer;
        if (packEl) packEl.textContent = current.pack;
        if (timeEl) timeEl.textContent = current.time;

        toastEl.classList.add('show');

        setTimeout(() => {
            toastEl.classList.remove('show');
        }, 5500);
    }

    function startToastLoop() {
        setTimeout(() => {
            showToast();
            setInterval(showToast, 18000);
        }, 3000);
    }
}

// ==========================================================================
// Interactive FPS Gain Simulator
// ==========================================================================
function initFpsCalculator() {
    const gameSelect = document.getElementById('calcGame');
    const gpuSelect = document.getElementById('calcGpu');
    const packSelect = document.getElementById('calcPack');
    const beforeFpsEl = document.getElementById('calcBeforeFps');
    const afterFpsEl = document.getElementById('calcAfterFps');
    const percentEl = document.getElementById('calcPercentBoost');
    const latencyEl = document.getElementById('calcLatencyDrop');
    const progressBar = document.getElementById('calcProgressBar');

    if (!gameSelect || !beforeFpsEl) return;

    const gameData = {
        'valorant': { base: [110, 210, 340], latency: 22 },
        'cs2': { base: [85, 160, 260], latency: 26 },
        'fortnite': { base: [75, 140, 240], latency: 30 },
        'warzone': { base: [50, 95, 155], latency: 38 },
        'fivem': { base: [60, 105, 165], latency: 34 },
        'apex': { base: [70, 130, 210], latency: 28 }
    };

    const packBoost = {
        'starter': { mult: 1.22, latCut: 10, name: "Starter Pack" },
        'ultra': { mult: 1.55, latCut: 22, name: "Competitive Ultra" },
        'network': { mult: 1.40, latCut: 26, name: "Zero Latency Pro" },
        'extreme': { mult: 1.80, latCut: 35, name: "Ultimate Extreme Suite" }
    };

    function updateCalculations() {
        const game = gameSelect.value;
        const gpuIndex = parseInt(gpuSelect.value, 10);
        const pack = packSelect.value;

        const info = gameData[game] || gameData['valorant'];
        const boost = packBoost[pack] || packBoost['ultra'];

        const baseFps = info.base[gpuIndex];
        const boostedFps = Math.round(baseFps * boost.mult);
        const percentIncrease = Math.round(((boostedFps - baseFps) / baseFps) * 100);
        const remainingLatency = Math.max(3, info.latency - boost.latCut);

        animateNumber(beforeFpsEl, parseInt(beforeFpsEl.textContent) || baseFps, baseFps);
        animateNumber(afterFpsEl, parseInt(afterFpsEl.textContent) || boostedFps, boostedFps);
        
        if (percentEl) percentEl.textContent = `+${percentIncrease}% FPS`;
        if (latencyEl) latencyEl.textContent = `${remainingLatency}ms`;
        
        if (progressBar) {
            const width = Math.min(100, (boostedFps / 450) * 100);
            progressBar.style.width = `${width}%`;
        }
    }

    function animateNumber(element, start, end) {
        if (start === end) {
            element.textContent = end;
            return;
        }
        let current = start;
        const step = end > start ? Math.ceil((end - start) / 10) : Math.floor((end - start) / 10);
        const timer = setInterval(() => {
            current += step;
            if ((step > 0 && current >= end) || (step < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = current;
        }, 20);
    }

    gameSelect.addEventListener('change', () => { ApexSound.playClick(); updateCalculations(); });
    gpuSelect.addEventListener('change', () => { ApexSound.playClick(); updateCalculations(); });
    packSelect.addEventListener('change', () => { ApexSound.playClick(); updateCalculations(); });

    updateCalculations();
}

// ==========================================================================
// AJAX Add to Cart with Audio Feedback
// ==========================================================================
function initAjaxAddToCart() {
    document.querySelectorAll('.btn-add-cart-ajax').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const prodId = this.getAttribute('data-product-id');
            const originalText = this.innerHTML;
            
            ApexSound.playClick();
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Adicionando...';
            this.disabled = true;

            fetch(`/cart/add/${prodId}?format=json`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                ApexSound.playSuccess();
                this.innerHTML = '<i class="bi bi-check-lg"></i> Adicionado!';
                this.classList.remove('btn-apex-primary');
                this.classList.add('btn-success');

                ['sidebarCartBadge', 'mobileCartBadge', 'navbarCartBadge'].forEach(id => {
                    const badge = document.getElementById(id);
                    if (badge) {
                        badge.textContent = data.cart_count;
                        badge.classList.remove('d-none');
                    }
                });

                showQuickAlert(data.message || 'Item adicionado ao seu carrinho!', 'success');

                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('btn-success');
                    this.classList.add('btn-apex-primary');
                    this.disabled = false;
                }, 2000);
            })
            .catch(() => {
                this.innerHTML = originalText;
                this.disabled = false;
                window.location.href = `/cart/add/${prodId}`;
            });
        });
    });
}

// ==========================================================================
// Copy to Clipboard
// ==========================================================================
function initCopyButtons() {
    document.querySelectorAll('.btn-copy-clip').forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-copy-target');
            const textToCopy = targetId ? document.getElementById(targetId)?.innerText || document.getElementById(targetId)?.value : this.getAttribute('data-copy-text');
            
            if (textToCopy) {
                navigator.clipboard.writeText(textToCopy.trim()).then(() => {
                    ApexSound.playSuccess();
                    const originalHtml = this.innerHTML;
                    this.innerHTML = '<i class="bi bi-check2"></i> Copiado!';
                    setTimeout(() => {
                        this.innerHTML = originalHtml;
                    }, 2000);
                });
            }
        });
    });
}

// ==========================================================================
// PIX Live Countdown Timer (10:00)
// ==========================================================================
function initPixTimer() {
    const timerDisplay = document.getElementById('pixTimerDisplay');
    if (!timerDisplay) return;

    let totalSeconds = 600; // 10 minutes

    function renderTime() {
        const mins = Math.floor(totalSeconds / 60);
        const secs = totalSeconds % 60;
        timerDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    renderTime();

    const interval = setInterval(() => {
        if (totalSeconds > 0) {
            totalSeconds--;
            renderTime();
        } else {
            clearInterval(interval);
            timerDisplay.textContent = '00:00 (Expirado)';
            timerDisplay.classList.remove('text-cyan');
            timerDisplay.classList.add('text-danger');
        }
    }, 1000);
}

// ==========================================================================
// Checkout Processing State Feedback
// ==========================================================================
function initCheckoutEnhancements() {
    const checkoutForm = document.getElementById('checkoutForm');
    const submitBtn = document.getElementById('btnSubmitCheckout');

    if (!checkoutForm || !submitBtn) return;

    checkoutForm.addEventListener('submit', function() {
        ApexSound.playSuccess();
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Processando e Gerando Licença...';
    });
}

// ==========================================================================
// Apex Bottleneck Scanner & Diagnostic Tool
// ==========================================================================
function initBottleneckScanner() {
    const btnStart = document.getElementById('btnStartScan');
    const idleState = document.getElementById('scanIdleState');
    const runningState = document.getElementById('scanRunningState');
    const resultState = document.getElementById('scanResultState');
    const progressBar = document.getElementById('scanProgressBar');
    const percentText = document.getElementById('scanPercentText');
    const terminalLogs = document.getElementById('scanTerminalLogs');

    if (!btnStart) return;

    btnStart.addEventListener('click', () => {
        ApexSound.playClick();

        if (idleState) idleState.classList.add('d-none');
        if (resultState) resultState.classList.add('d-none');
        if (runningState) {
            runningState.classList.remove('d-none');
            runningState.classList.add('d-flex');
        }

        btnStart.disabled = true;
        btnStart.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> ESCANEANDO GARGALOS...';

        const logs = [
            { pct: 15, msg: 'Inspecionando registradores de Core Parking do processador...', cls: 'active' },
            { pct: 40, msg: 'Clock Skew detectado: Timer do Kernel oscilando em 15.6ms...', cls: 'text-warning' },
            { pct: 65, msg: 'Mapeando fila de renderização DirectX e driver de vídeo...', cls: 'active' },
            { pct: 85, msg: 'Identificando processos fantasmas de telemetria e Xbox DVR...', cls: 'text-warning' },
            { pct: 100, msg: 'Varredura concluída. Compilando diagnóstico final...', cls: 'success' }
        ];

        let currentStep = 0;
        if (terminalLogs) terminalLogs.innerHTML = '<div class="scanner-log-line active"><i class="bi bi-terminal me-1"></i> Iniciando diagnóstico de kernel...</div>';

        const stepInterval = setInterval(() => {
            if (currentStep < logs.length) {
                const item = logs[currentStep];
                if (progressBar) progressBar.style.width = item.pct + '%';
                if (percentText) percentText.textContent = item.pct + '%';
                if (terminalLogs) {
                    const line = document.createElement('div');
                    line.className = `scanner-log-line ${item.cls}`;
                    line.innerHTML = `<i class="bi bi-chevron-right me-1"></i> ${item.msg}`;
                    terminalLogs.appendChild(line);
                    terminalLogs.scrollTop = terminalLogs.scrollHeight;
                }
                currentStep++;
            } else {
                clearInterval(stepInterval);
                setTimeout(() => {
                    if (runningState) {
                        runningState.classList.remove('d-flex');
                        runningState.classList.add('d-none');
                    }
                    if (resultState) resultState.classList.remove('d-none');
                    btnStart.disabled = false;
                    btnStart.innerHTML = '<i class="bi bi-arrow-repeat me-2"></i> REPETIR VARREDURA';
                    ApexSound.playSuccess();
                }, 600);
            }
        }, 450);
    });
}

// ==========================================================================
// Mystery Drop Gamer Lootbox Modal
// ==========================================================================
function initMysteryDropModal() {
    const triggerVault = document.getElementById('lootboxTrigger');
    const openBtn = document.getElementById('btnOpenLootbox');
    const closedState = document.getElementById('lootboxClosedState');
    const openedState = document.getElementById('lootboxOpenedState');

    if (!openBtn || !triggerVault) return;

    function handleOpenDrop() {
        triggerVault.classList.add('lootbox-shake');
        openBtn.disabled = true;
        openBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Desbloqueando...';
        ApexSound.playClick();

        setTimeout(() => {
            triggerVault.classList.remove('lootbox-shake');
            if (closedState) closedState.classList.add('d-none');
            if (openedState) openedState.classList.remove('d-none');
            ApexSound.playSuccess();
        }, 1100);
    }

    triggerVault.addEventListener('click', handleOpenDrop);
    openBtn.addEventListener('click', handleOpenDrop);
}

// ==========================================================================
// Helper quick alert
// ==========================================================================
function showQuickAlert(msg, type = 'success') {
    const container = document.getElementById('globalAlertContainer');
    if (!container) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show glass-card border-0 shadow-lg text-white mb-2`;
    alert.innerHTML = `
        <div class="d-flex align-items-center gap-2">
            <i class="bi bi-lightning-charge-fill text-info"></i>
            <span>${msg}</span>
        </div>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
    `;
    container.appendChild(alert);

    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 300);
    }, 4000);
}
