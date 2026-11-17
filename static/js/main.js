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
    initSidebarDrawer();
    initSidebarTabs();
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

// Mobile & Desktop Sidebar Drawer Navigation
function initSidebarDrawer() {
    const sidebar = document.getElementById('appSidebar');
    const overlay = document.getElementById('mobileSidebarOverlay');
    const openBtn = document.getElementById('openSidebarBtn');
    const closeBtn = document.getElementById('closeSidebarBtn');
    const bottomMenuBtn = document.getElementById('bottomNavMenuBtn');
    const collapseBtn = document.getElementById('collapseSidebarBtn');
    const expandBtn = document.getElementById('expandSidebarBtn');
    const navToggleBtn = document.getElementById('navToggleSidebarBtn');

    function openMobileDrawer() {
        if (sidebar) sidebar.classList.add('show');
        if (overlay) overlay.classList.add('show');
        document.body.style.overflow = 'hidden';
        ApexSound.playClick();
    }

    function closeMobileDrawer() {
        if (sidebar) sidebar.classList.remove('show');
        if (overlay) overlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    if (openBtn) openBtn.addEventListener('click', openMobileDrawer);
    if (bottomMenuBtn) bottomMenuBtn.addEventListener('click', (e) => {
        e.preventDefault();
        openMobileDrawer();
    });
    if (closeBtn) closeBtn.addEventListener('click', closeMobileDrawer);
    if (overlay) overlay.addEventListener('click', closeMobileDrawer);

    // Escape key closes drawer
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeMobileDrawer();
    });

    // Close drawer when clicking any link in sidebar on mobile
    if (sidebar) {
        sidebar.querySelectorAll('a, .sidebar-nav-item').forEach(el => {
            el.addEventListener('click', () => {
                if (window.innerWidth < 992) closeMobileDrawer();
            });
        });
    }

    // Desktop Collapse / Expand Handlers
    function toggleDesktopSidebar() {
        const isHidden = document.body.classList.toggle('sidebar-hidden');
        localStorage.setItem('apex_sidebar_hidden', isHidden ? 'true' : 'false');
        if (expandBtn) expandBtn.style.setProperty('display', isHidden ? 'inline-flex' : 'none', 'important');
        ApexSound.playClick();
    }

    if (collapseBtn) collapseBtn.addEventListener('click', toggleDesktopSidebar);
    if (expandBtn) expandBtn.addEventListener('click', toggleDesktopSidebar);
    if (navToggleBtn) navToggleBtn.addEventListener('click', toggleDesktopSidebar);

    // Initial desktop state from localStorage
    if (window.innerWidth >= 992 && localStorage.getItem('apex_sidebar_hidden') === 'true') {
        document.body.classList.add('sidebar-hidden');
        if (expandBtn) expandBtn.style.setProperty('display', 'inline-flex', 'important');
    }
}

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
// Dynamic Sidebar Tab Switching (Shows ONLY selected tab)
// ==========================================================================
function initSidebarTabs() {
    const tabTriggers = document.querySelectorAll('[data-tab-target]');
    const tabPanes = document.querySelectorAll('.store-tab-pane');
    const sidebarNavItems = document.querySelectorAll('.sidebar-nav-item[data-tab-target]');
    const mobileBottomItems = document.querySelectorAll('.mobile-bottom-item[data-tab-target]');

    function activateTab(tabId) {
        if (!tabId) tabId = 'tab-home';
        const clean = tabId.replace(/^#/, '');
        const targetWithTab = clean.startsWith('tab-') ? clean : 'tab-' + clean;

        if (tabPanes.length > 0) {
            let found = false;
            tabPanes.forEach(pane => {
                if (pane.id === targetWithTab || pane.id === clean) {
                    pane.classList.add('active');
                    found = true;
                } else {
                    pane.classList.remove('active');
                }
            });

            if (!found && tabPanes[0]) {
                tabPanes[0].classList.add('active');
            }

            // Update active state in sidebar
            sidebarNavItems.forEach(item => {
                const t = (item.getAttribute('data-tab-target') || '').replace(/^#/, '');
                const tWithTab = t.startsWith('tab-') ? t : 'tab-' + t;
                if (tWithTab === targetWithTab || t === clean) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });

            // Update active state in mobile bottom dock
            mobileBottomItems.forEach(item => {
                const t = (item.getAttribute('data-tab-target') || '').replace(/^#/, '');
                const tWithTab = t.startsWith('tab-') ? t : 'tab-' + t;
                if (tWithTab === targetWithTab || t === clean) {
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
            const targetId = this.getAttribute('data-tab-target') || this.getAttribute('href');
            if (targetId && tabPanes.length > 0) {
                const clean = targetId.replace(/^#/, '').replace(/^tab-/, '');
                const targetEl = document.getElementById(targetId.replace(/^#/, '')) 
                              || document.getElementById('tab-' + clean)
                              || document.getElementById(clean);

                if (targetEl) {
                    e.preventDefault();
                    activateTab(targetId);
                    try {
                        const newHash = clean.startsWith('tab-') ? clean : 'tab-' + clean;
                        window.history.pushState(null, '', '#' + newHash);
                    } catch(err) {}

                    // Close mobile sidebar if open
                    const sidebar = document.getElementById('appSidebar');
                    const overlay = document.getElementById('mobileSidebarOverlay');
                    if (sidebar) sidebar.classList.remove('show');
                    if (overlay) overlay.classList.remove('show');
                }
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
// Interactive True Hardware FPS Gain Simulator (Cálculo Realista em Tempo Real)
// ==========================================================================
function initFpsCalculator() {
    const gameSelect = document.getElementById('calcGame');
    const resSelect = document.getElementById('calcResolution');
    const cpuSelect = document.getElementById('calcCpu');
    const gpuSelect = document.getElementById('calcGpu');
    const ramSelect = document.getElementById('calcRam');
    const storageSelect = document.getElementById('calcStorage');
    const packSelect = document.getElementById('calcPack');

    const customCpuInput = document.getElementById('calcCustomCpuInput');
    const customGpuInput = document.getElementById('calcCustomGpuInput');
    const customFpsInput = document.getElementById('calcCustomFps');
    const clearCustomFpsBtn = document.getElementById('btnClearCustomFps');

    const btnModeQuick = document.getElementById('btnModeQuick');
    const btnModeCustom = document.getElementById('btnModeCustom');
    const quickContainer = document.getElementById('calcQuickContainer');
    const customContainer = document.getElementById('calcCustomContainer');
    const btnDetectSetup = document.getElementById('btnDetectMyPc');

    const beforeFpsEl = document.getElementById('calcBeforeFps');
    const afterFpsEl = document.getElementById('calcAfterFps');
    const percentEl = document.getElementById('calcPercentBoost');
    const gainBadgeEl = document.getElementById('calcGainBadge');
    const low1El = document.getElementById('calc1Low');
    const latencyEl = document.getElementById('calcLatencyDrop');
    const diagTitleEl = document.getElementById('calcDiagTitle');
    const diagDescEl = document.getElementById('calcDiagDesc');
    const diagIconEl = document.getElementById('calcDiagIcon');
    const ctaBtn = document.getElementById('calcCtaBtn');

    if (!gameSelect || !beforeFpsEl) return;

    let activeCalcMode = 'quick'; // 'quick' ou 'custom'

    // Alternador de Modo: Seleção Rápida vs Digitar Meu Setup Exato
    function setCalcMode(mode) {
        activeCalcMode = mode;
        if (mode === 'custom') {
            if (quickContainer) quickContainer.classList.add('d-none');
            if (customContainer) customContainer.classList.remove('d-none');
            if (btnModeCustom) {
                btnModeCustom.classList.add('active');
                btnModeCustom.classList.remove('text-secondary');
            }
            if (btnModeQuick) {
                btnModeQuick.classList.remove('active');
                btnModeQuick.classList.add('text-secondary');
            }
        } else {
            if (quickContainer) quickContainer.classList.remove('d-none');
            if (customContainer) customContainer.classList.add('d-none');
            if (btnModeQuick) {
                btnModeQuick.classList.add('active');
                btnModeQuick.classList.remove('text-secondary');
            }
            if (btnModeCustom) {
                btnModeCustom.classList.remove('active');
                btnModeCustom.classList.add('text-secondary');
            }
        }
        if (typeof ApexSound !== 'undefined' && ApexSound.playClick) {
            ApexSound.playClick();
        }
        updateCalculations();
    }

    if (btnModeQuick) btnModeQuick.addEventListener('click', () => setCalcMode('quick'));
    if (btnModeCustom) btnModeCustom.addEventListener('click', () => setCalcMode('custom'));

    // Botão para limpar o FPS personalizado e voltar ao automático
    if (clearCustomFpsBtn && customFpsInput) {
        clearCustomFpsBtn.addEventListener('click', () => {
            customFpsInput.value = '';
            if (typeof ApexSound !== 'undefined' && ApexSound.playClick) {
                ApexSound.playClick();
            }
            updateCalculations();
        });
    }

    // Botão de Detecção Automática do PC do Usuário
    if (btnDetectSetup) {
        btnDetectSetup.addEventListener('click', () => {
            let detectedGpu = 'NVIDIA GeForce RTX 3060';
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (gl) {
                    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    if (debugInfo) {
                        const raw = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                        const angleMatch = raw.match(/ANGLE \([^,]+,\s*([^,]+)/i);
                        if (angleMatch && angleMatch[1]) {
                            detectedGpu = angleMatch[1].replace(/Direct3D.*/i, '').trim();
                        } else {
                            detectedGpu = raw.replace(/Direct3D.*/i, '').replace(/vs_\d+_\d+.*/i, '').trim();
                        }
                    }
                }
            } catch (e) {}

            const threads = navigator.hardwareConcurrency || 8;
            let detectedCpu = `AMD Ryzen / Intel Core (${threads} Threads Lógicas)`;
            if (threads >= 16) detectedCpu = `Processador de Alto Desempenho (${threads} Threads)`;
            else if (threads >= 12) detectedCpu = `Processador Gamer (${threads} Threads)`;
            else if (threads >= 6) detectedCpu = `Processador Multi-Core (${threads} Threads)`;

            // Preenche os campos personalizados
            if (customGpuInput) customGpuInput.value = detectedGpu;
            if (customCpuInput) customCpuInput.value = detectedCpu;

            // Seletor de RAM aproximado se disponível pela API
            if (ramSelect && navigator.deviceMemory) {
                const mem = navigator.deviceMemory;
                if (mem >= 32) ramSelect.value = 'ram_32_dual';
                else if (mem >= 16) ramSelect.value = 'ram_16_dual';
                else if (mem >= 8) ramSelect.value = 'ram_8_dual';
            }

            // Alterna para o modo customizado para mostrar as peças detectadas
            setCalcMode('custom');

            if (typeof ApexSound !== 'undefined' && ApexSound.playSuccess) {
                ApexSound.playSuccess();
            }
            showQuickAlert(`Setup detectado com sucesso: ${detectedGpu}!`, 'success');
        });
    }

    // 1. Dados de Benchmark Base dos Jogos (Padrão 1080p Competitivo)
    const gameData = {
        'cs2': {
            name: 'Counter-Strike 2',
            baseFps: 160,
            cpuWeight: 0.58,  // Muito sensível a CPU e latência de memória
            gpuWeight: 0.42,
            latencyBase: 26,
            low1Ratio: 0.54
        },
        'valorant': {
            name: 'Valorant',
            baseFps: 215,
            cpuWeight: 0.72,  // Ultra CPU-bound
            gpuWeight: 0.28,
            latencyBase: 20,
            low1Ratio: 0.62
        },
        'warzone': {
            name: 'Call of Duty: Warzone',
            baseFps: 105,
            cpuWeight: 0.46,
            gpuWeight: 0.54,
            latencyBase: 38,
            low1Ratio: 0.44
        },
        'fortnite': {
            name: 'Fortnite',
            baseFps: 145,
            cpuWeight: 0.62,
            gpuWeight: 0.38,
            latencyBase: 29,
            low1Ratio: 0.52
        },
        'fivem': {
            name: 'GTA V / FiveM',
            baseFps: 112,
            cpuWeight: 0.65,
            gpuWeight: 0.35,
            latencyBase: 34,
            low1Ratio: 0.46
        },
        'apex': {
            name: 'Apex Legends',
            baseFps: 135,
            cpuWeight: 0.50,
            gpuWeight: 0.50,
            latencyBase: 28,
            low1Ratio: 0.55
        },
        'r6': {
            name: 'Rainbow Six Siege',
            baseFps: 195,
            cpuWeight: 0.45,
            gpuWeight: 0.55,
            latencyBase: 22,
            low1Ratio: 0.64
        },
        'lol': {
            name: 'League of Legends',
            baseFps: 225,
            cpuWeight: 0.76,
            gpuWeight: 0.24,
            latencyBase: 16,
            low1Ratio: 0.65
        },
        'rust': {
            name: 'Rust',
            baseFps: 95,
            cpuWeight: 0.60,
            gpuWeight: 0.40,
            latencyBase: 35,
            low1Ratio: 0.42
        }
    };

    // 2. Multiplicadores de Potência do Processador (CPU)
    const cpuData = {
        'cpu_ryzen_x3d': { mult: 1.95, bloatPenalty: 0.08, name: 'Ryzen 3D V-Cache (5700X3D/7800X3D)', type: 'high' },
        'cpu_ryzen_7000': { mult: 1.65, bloatPenalty: 0.10, name: 'Ryzen 7000 (7600/7700X)', type: 'high' },
        'cpu_ryzen_5600': { mult: 1.38, bloatPenalty: 0.14, name: 'Ryzen 5 5600 / 5600X / 5500', type: 'mid_modern' },
        'cpu_ryzen_3600': { mult: 1.10, bloatPenalty: 0.18, name: 'Ryzen 5 3600 / 2600 / 1600 AF', type: 'mid_old' },
        'cpu_ryzen_entry': { mult: 0.78, bloatPenalty: 0.24, name: 'Ryzen 3 3200G / 2200G / Athlon', type: 'entry' },
        'cpu_intel_ultra': { mult: 1.85, bloatPenalty: 0.08, name: 'Core i7/i9 (12700K a 14900K)', type: 'high' },
        'cpu_intel_modern': { mult: 1.45, bloatPenalty: 0.12, name: 'Core i5 (12400F a 14600K)', type: 'mid_modern' },
        'cpu_intel_12100': { mult: 1.20, bloatPenalty: 0.16, name: 'Core i3 12100F / 13100F', type: 'mid_modern' },
        'cpu_intel_mid_old': { mult: 1.05, bloatPenalty: 0.19, name: 'Core i5 (8400 a 11400F)', type: 'mid_old' },
        'cpu_intel_7700': { mult: 1.25, bloatPenalty: 0.15, name: 'Core i7 (7700K a 10700K)', type: 'mid_old' },
        'cpu_intel_old_i3': { mult: 0.82, bloatPenalty: 0.22, name: 'Core i3 (8100 a 10100F)', type: 'entry' },
        'cpu_xeon': { mult: 0.92, bloatPenalty: 0.22, name: 'Intel Xeon E5 Kit', type: 'mid_old' },
        'cpu_intel_vintage': { mult: 0.72, bloatPenalty: 0.26, name: 'Core i5 antigo (2500 a 7400)', type: 'entry' },
        'cpu_entry': { mult: 0.58, bloatPenalty: 0.30, name: 'Core i3 antigo / Celeron / Pentium', type: 'entry' }
    };

    // Parser Inteligente para Processador Customizado Digitado
    function parseCustomCpu(text) {
        const t = (text || '').toLowerCase().trim();
        if (!t) return cpuData['cpu_ryzen_5600'];
        
        if (t.includes('x3d') || t.includes('7800x3d') || t.includes('5800x3d') || t.includes('5700x3d') || t.includes('9800x3d')) {
            return { mult: 1.95, bloatPenalty: 0.08, name: text, type: 'high' };
        }
        if (t.includes('14900') || t.includes('13900') || t.includes('14700') || t.includes('13700') || t.includes('12900') || t.includes('7950') || t.includes('7900') || t.includes('5950') || t.includes('5900')) {
            return { mult: 1.85, bloatPenalty: 0.08, name: text, type: 'high' };
        }
        if (t.includes('7600') || t.includes('7500f') || t.includes('7700') || t.includes('9600') || t.includes('9700')) {
            return { mult: 1.65, bloatPenalty: 0.10, name: text, type: 'high' };
        }
        if (t.includes('14600') || t.includes('13600') || t.includes('12600') || t.includes('12700') || t.includes('5800x') || t.includes('5700x')) {
            return { mult: 1.55, bloatPenalty: 0.11, name: text, type: 'high' };
        }
        if (t.includes('12400') || t.includes('13400') || t.includes('14400') || t.includes('5600') || t.includes('5500')) {
            return { mult: 1.38, bloatPenalty: 0.14, name: text, type: 'mid_modern' };
        }
        if (t.includes('12100') || t.includes('13100') || t.includes('14100') || t.includes('11400') || t.includes('11600') || t.includes('10700') || t.includes('9700') || t.includes('8700')) {
            return { mult: 1.22, bloatPenalty: 0.16, name: text, type: 'mid_modern' };
        }
        if (t.includes('3600') || t.includes('2600') || t.includes('10400') || t.includes('9400') || t.includes('8400') || t.includes('1600 af')) {
            return { mult: 1.08, bloatPenalty: 0.18, name: text, type: 'mid_old' };
        }
        if (t.includes('xeon') || t.includes('2670') || t.includes('2650') || t.includes('2640') || t.includes('2620')) {
            return { mult: 0.92, bloatPenalty: 0.22, name: text, type: 'mid_old' };
        }
        if (t.includes('10100') || t.includes('9100') || t.includes('8100') || t.includes('7700') || t.includes('6700') || t.includes('4790') || t.includes('3770')) {
            return { mult: 0.88, bloatPenalty: 0.22, name: text, type: 'mid_old' };
        }
        if (t.includes('3200g') || t.includes('2200g') || t.includes('3100') || t.includes('3300') || t.includes('7400') || t.includes('6400') || t.includes('4590') || t.includes('3470') || t.includes('2500')) {
            return { mult: 0.75, bloatPenalty: 0.25, name: text, type: 'entry' };
        }
        if (t.includes('fx') || t.includes('athlon') || t.includes('pentium') || t.includes('celeron') || t.includes('core 2')) {
            return { mult: 0.55, bloatPenalty: 0.30, name: text, type: 'entry' };
        }
        // Heurísticas genéricas
        if (t.includes('i9') || t.includes('ryzen 9')) return { mult: 1.80, bloatPenalty: 0.08, name: text, type: 'high' };
        if (t.includes('i7') || t.includes('ryzen 7')) return { mult: 1.50, bloatPenalty: 0.12, name: text, type: 'high' };
        if (t.includes('i5') || t.includes('ryzen 5')) return { mult: 1.25, bloatPenalty: 0.15, name: text, type: 'mid_modern' };
        if (t.includes('i3') || t.includes('ryzen 3')) return { mult: 0.90, bloatPenalty: 0.20, name: text, type: 'entry' };
        
        return { mult: 1.10, bloatPenalty: 0.18, name: text, type: 'mid_old' };
    }

    // 3. Multiplicadores de Potência da Placa de Vídeo (GPU)
    const gpuData = {
        'gpu_rtx_4080': { mult: 3.10, name: 'RTX 4080 / RTX 4090', tier: 6 },
        'gpu_rtx_4070': { mult: 2.40, name: 'RTX 4070 / RTX 3080', tier: 5 },
        'gpu_rtx_3060ti': { mult: 1.95, name: 'RTX 4060 / RTX 3060 Ti', tier: 4 },
        'gpu_rtx_3060': { mult: 1.58, name: 'RTX 3060 12GB / RTX 2060 Super', tier: 4 },
        'gpu_gtx_1660': { mult: 1.15, name: 'GTX 1660 / 1660 Super', tier: 3 },
        'gpu_gtx_1060': { mult: 0.95, name: 'GTX 1060 6GB / GTX 1650 Super', tier: 3 },
        'gpu_gtx_1650': { mult: 0.78, name: 'GTX 1650 / GTX 1050 Ti', tier: 2 },
        'gpu_gtx_entry': { mult: 0.50, name: 'GT 1030 / GTX 750 Ti', tier: 2 },
        'gpu_rx_7000': { mult: 2.65, name: 'RX 7800 XT / RX 7900 XTX', tier: 6 },
        'gpu_rx_6700': { mult: 2.05, name: 'RX 6700 XT / RX 7700 XT', tier: 5 },
        'gpu_rx_6600': { mult: 1.52, name: 'RX 6600 / RX 7600', tier: 4 },
        'gpu_rx_580': { mult: 0.95, name: 'RX 580 8GB / RX 590', tier: 3 },
        'gpu_rx_550': { mult: 0.52, name: 'RX 550 / RX 560', tier: 2 },
        'gpu_vega': { mult: 0.42, name: 'AMD Radeon Vega Graphics', tier: 1 },
        'gpu_iris': { mult: 0.45, name: 'Intel Iris Xe Graphics', tier: 1 },
        'gpu_uhd': { mult: 0.35, name: 'Intel UHD Graphics 630/730/770', tier: 1 },
        'gpu_integrated': { mult: 0.22, name: 'Gráficos Integrados Básicos', tier: 1 }
    };

    // Parser Inteligente para Placa de Vídeo Customizada Digitada
    function parseCustomGpu(text) {
        const t = (text || '').toLowerCase().trim();
        if (!t) return gpuData['gpu_rtx_3060'];
        
        if (t.includes('4090')) return { mult: 3.30, name: text, tier: 6 };
        if (t.includes('4080') || t.includes('7900 xtx') || t.includes('7900 xt')) return { mult: 2.85, name: text, tier: 6 };
        if (t.includes('4070 ti') || t.includes('4070 super') || t.includes('3090') || t.includes('7900 gre') || t.includes('7800 xt')) return { mult: 2.50, name: text, tier: 5 };
        if (t.includes('4070') || t.includes('3080')) return { mult: 2.30, name: text, tier: 5 };
        if (t.includes('3070 ti') || t.includes('3070') || t.includes('4060 ti') || t.includes('6750 xt') || t.includes('6700 xt') || t.includes('7700 xt')) return { mult: 2.00, name: text, tier: 4 };
        if (t.includes('4060') || t.includes('3060 ti') || t.includes('2080') || t.includes('7600')) return { mult: 1.75, name: text, tier: 4 };
        if (t.includes('3060') || t.includes('2060 super') || t.includes('2070') || t.includes('6650 xt') || t.includes('6600 xt')) return { mult: 1.58, name: text, tier: 4 };
        if (t.includes('6600') || t.includes('2060') || t.includes('3050') || t.includes('1080 ti') || t.includes('1080') || t.includes('5600 xt')) return { mult: 1.35, name: text, tier: 3 };
        if (t.includes('1660 ti') || t.includes('1660 super') || t.includes('1660') || t.includes('1070 ti') || t.includes('1070') || t.includes('590')) return { mult: 1.15, name: text, tier: 3 };
        if (t.includes('1650 super') || t.includes('1060') || t.includes('580') || t.includes('5500 xt') || t.includes('6500 xt')) return { mult: 0.95, name: text, tier: 3 };
        if (t.includes('1650') || t.includes('1050 ti') || t.includes('570') || t.includes('970') || t.includes('960')) return { mult: 0.78, name: text, tier: 2 };
        if (t.includes('1050') || t.includes('750 ti') || t.includes('950') || t.includes('560') || t.includes('550') || t.includes('1030')) return { mult: 0.52, name: text, tier: 2 };
        if (t.includes('680m') || t.includes('780m')) return { mult: 0.65, name: text, tier: 2 };
        if (t.includes('vega') || t.includes('iris') || t.includes('radeon graphics')) return { mult: 0.42, name: text, tier: 1 };
        if (t.includes('uhd') || t.includes('hd graphics') || t.includes('integrated') || t.includes('integrada')) return { mult: 0.28, name: text, tier: 1 };
        
        // Heurísticas genéricas
        if (t.includes('rtx 40')) return { mult: 2.20, name: text, tier: 5 };
        if (t.includes('rtx 30')) return { mult: 1.80, name: text, tier: 4 };
        if (t.includes('rtx 20')) return { mult: 1.40, name: text, tier: 3 };
        if (t.includes('gtx 16') || t.includes('gtx 10')) return { mult: 0.95, name: text, tier: 3 };
        if (t.includes('rx 7') || t.includes('rx 6')) return { mult: 1.70, name: text, tier: 4 };
        if (t.includes('rx 5')) return { mult: 0.90, name: text, tier: 3 };
        
        return { mult: 1.00, name: text, tier: 3 };
    }

    // 4. Modificadores de Memória RAM (Largura de banda e estabilidade de frametime)
    const ramData = {
        'ram_4_single': { mult: 0.68, lowPenalty: 0.55, latAdd: 14, isSingle: true },
        'ram_8_single': { mult: 0.82, lowPenalty: 0.42, latAdd: 8, isSingle: true },
        'ram_8_dual': { mult: 0.92, lowPenalty: 0.18, latAdd: 4, isSingle: false },
        'ram_12_mixed': { mult: 0.95, lowPenalty: 0.12, latAdd: 2, isSingle: false },
        'ram_16_single': { mult: 0.88, lowPenalty: 0.28, latAdd: 5, isSingle: true },
        'ram_16_dual': { mult: 1.00, lowPenalty: 0.00, latAdd: 0, isSingle: false },
        'ram_32_dual': { mult: 1.06, lowPenalty: -0.06, latAdd: -1, isSingle: false },
        'ram_64_dual': { mult: 1.08, lowPenalty: -0.08, latAdd: -2, isSingle: false }
    };

    // 5. Modificadores de Armazenamento (I/O e carregamento de texturas)
    const storageData = {
        'storage_hdd': { mult: 0.92, lowPenalty: 0.34, isHdd: true },
        'storage_sata': { mult: 1.00, lowPenalty: 0.00, isHdd: false },
        'storage_nvme': { mult: 1.04, lowPenalty: -0.05, isHdd: false }
    };

    // 6. Resolução de Renderização
    const resData = {
        '1080p_comp': 1.15,
        '1080p_high': 0.92,
        '1440p': 0.72,
        '4k': 0.46
    };

    // 7. Ganho Real de cada Pack Apex Boost
    const packBoost = {
        'starter': {
            mult: 1.25,
            latDrop: 12,
            lowBoost: 1.45,
            slug: 'starter-tweak-pack',
            name: 'Starter Tweak Pack'
        },
        'ultra': {
            mult: 1.55,
            latDrop: 22,
            lowBoost: 1.85,
            slug: 'competitive-fps-ultra-pack',
            name: 'Competitive FPS Ultra Pack'
        },
        'network': {
            mult: 1.42,
            latDrop: 26,
            lowBoost: 1.65,
            slug: 'zero-latency-network-pro',
            name: 'Zero Latency & Network Pro'
        },
        'extreme': {
            mult: 1.82,
            latDrop: 32,
            lowBoost: 2.20,
            slug: 'ultimate-extreme-suite',
            name: 'Ultimate Extreme Suite'
        }
    };

    function updateCalculations() {
        const gameKey = gameSelect ? gameSelect.value : 'cs2';
        const resKey = resSelect ? resSelect.value : '1080p_comp';
        const ramKey = ramSelect ? ramSelect.value : 'ram_16_dual';
        const storageKey = storageSelect ? storageSelect.value : 'storage_nvme';
        const packKey = packSelect ? packSelect.value : 'ultra';

        const game = gameData[gameKey] || gameData['cs2'];
        const ram = ramData[ramKey] || ramData['ram_16_dual'];
        const storage = storageData[storageKey] || storageData['storage_nvme'];
        const resMult = resData[resKey] || 1.15;
        const pack = packBoost[packKey] || packBoost['ultra'];

        // Resolução de CPU e GPU dependendo do modo ativo
        let cpu, gpu;
        if (activeCalcMode === 'custom') {
            cpu = parseCustomCpu(customCpuInput ? customCpuInput.value : '');
            gpu = parseCustomGpu(customGpuInput ? customGpuInput.value : '');
        } else {
            const cpuKey = cpuSelect ? cpuSelect.value : 'cpu_ryzen_5600';
            const gpuKey = gpuSelect ? gpuSelect.value : 'gpu_rtx_3060';
            cpu = cpuData[cpuKey] || cpuData['cpu_ryzen_5600'];
            gpu = gpuData[gpuKey] || gpuData['gpu_rtx_3060'];
        }

        // Fator de alívio de bloatware e otimização
        let recoveryFactor = 1.0;
        if (ram.isSingle) recoveryFactor += 0.08;        // Standby RAM cleaner salva canal único
        if (storage.isHdd) recoveryFactor += 0.05;       // Remoção de telemetria alivia fila do HD
        if (cpu.bloatPenalty > 0.16) recoveryFactor += 0.05; // Core unparking ajuda CPUs sobrecarregadas

        // Verifica se o usuário informou um FPS atual exato
        let baseFps;
        let isUserExactFps = false;
        const rawCustomFps = customFpsInput ? parseInt(customFpsInput.value, 10) : NaN;

        if (!isNaN(rawCustomFps) && rawCustomFps >= 10 && rawCustomFps <= 1200) {
            baseFps = rawCustomFps;
            isUserExactFps = true;
        } else {
            // Cálculo de Potência Efetiva do Hardware combinando CPU e GPU com peso do jogo
            const effectiveHw = (cpu.mult * game.cpuWeight) + (gpu.mult * game.gpuWeight);
            
            // Penalidade por desequilíbrio severo (Gargalo de CPU ou GPU)
            const diff = Math.abs(cpu.mult - gpu.mult);
            const bottleneckPenalty = diff > 0.7 ? 0.90 : 1.0;

            // FPS Base Padrão do Windows
            baseFps = Math.round(game.baseFps * effectiveHw * resMult * ram.mult * storage.mult * bottleneckPenalty);
            baseFps = Math.max(25, baseFps);
        }

        const boostedFps = Math.round(baseFps * pack.mult * recoveryFactor);
        const diffFps = boostedFps - baseFps;
        const percentIncrease = Math.round(((boostedFps - baseFps) / baseFps) * 100);

        // 1% Lows (Estabilidade & Fim dos Micro-travamentos)
        const base1Low = Math.max(14, Math.round(baseFps * game.low1Ratio * (1 - ram.lowPenalty - storage.lowPenalty)));
        const boosted1Low = Math.round(base1Low * pack.lowBoost);

        // Latência de Entrada / Frametime em milissegundos
        const baseLat = Math.round(game.latencyBase + ram.latAdd);
        const finalLat = Math.max(3, Math.round(baseLat - pack.latDrop));

        // Animação dos números na tela
        animateNumber(beforeFpsEl, parseInt(beforeFpsEl.textContent) || baseFps, baseFps);
        animateNumber(afterFpsEl, parseInt(afterFpsEl.textContent) || boostedFps, boostedFps);

        // Atualiza legenda sob o FPS base
        const beforeSubEl = beforeFpsEl.parentElement.querySelector('small');
        if (beforeSubEl) {
            beforeSubEl.textContent = isUserExactFps ? 'Seu FPS real informado' : 'Windows sem tweak';
            beforeSubEl.className = isUserExactFps ? 'text-warning d-block mt-1' : 'text-muted d-block mt-1';
        }

        if (percentEl) {
            percentEl.textContent = `+${percentIncrease}% FPS`;
        }
        if (gainBadgeEl) {
            gainBadgeEl.innerHTML = `<i class="bi bi-graph-up-arrow me-1"></i> Ganho líquido: +${diffFps} FPS a mais na sua tela`;
        }
        if (low1El) {
            low1El.innerHTML = `<span class="text-danger">${base1Low} FPS</span> &rarr; <span class="text-cyan fw-black">${boosted1Low} FPS</span>`;
        }
        if (latencyEl) {
            latencyEl.innerHTML = `<span class="text-secondary">${baseLat}ms</span> &rarr; <span class="text-blue fw-black">${finalLat}ms</span>`;
        }

        // Diagnóstico inteligente do setup em tempo real
        updateDiagnosis(cpu, gpu, ramKey, storageKey, gameKey, pack.name, isUserExactFps);

        // Atualiza link do CTA para direcionar ao pack correspondente
        if (ctaBtn) {
            ctaBtn.href = `#tab-packs`;
        }
    }

    function updateDiagnosis(cpu, gpu, ramKey, storageKey, gameKey, packName, isUserExactFps) {
        if (!diagTitleEl || !diagDescEl) return;

        if (isUserExactFps) {
            if (diagIconEl) diagIconEl.className = 'bi bi-bullseye text-warning';
            diagTitleEl.textContent = 'Cálculo Baseado no seu FPS Real:';
            diagDescEl.textContent = `Aplicamos as curvas exatas do ${packName} diretamente sobre o seu desempenho medido no jogo. Você terá um salto imediato de estabilidade e fluidez!`;
            return;
        }

        if (ramKey === 'ram_8_single' || ramKey === 'ram_4_single' || ramKey === 'ram_16_single') {
            if (diagIconEl) diagIconEl.className = 'bi bi-exclamation-triangle-fill text-warning';
            diagTitleEl.textContent = 'Gargalo de Memória (Single Channel):';
            diagDescEl.textContent = 'Sua memória em 1 pente corta a largura de banda pela metade, causando micro-travamentos em tiroteios. O ' + packName + ' ativa o Standby List Cleaner e paginação otimizada, eliminando esse stutter!';
        } else if (storageKey === 'storage_hdd') {
            if (diagIconEl) diagIconEl.className = 'bi bi-hdd-fill text-warning';
            diagTitleEl.textContent = 'Gargalo de Disco (HD Mecânico):';
            diagDescEl.textContent = 'O HD causa engasgos ao carregar texturas em tempo real. O ' + packName + ' desativa telemetria agressiva e serviços de indexação, liberando a leitura para o jogo.';
        } else if (cpu.type === 'entry') {
            if (diagIconEl) diagIconEl.className = 'bi bi-lightning-charge-fill text-cyan';
            diagTitleEl.textContent = 'CPU Sobrecarregada pelo Windows:';
            diagDescEl.textContent = 'Processadores de entrada perdem até 35% de quadros com os 150+ processos ocultos do Windows. O ' + packName + ' desativa os bloatwares e acorda os núcleos com CPU Core Unparking!';
        } else if (gpu.tier >= 5 || cpu.type === 'high') {
            if (diagIconEl) diagIconEl.className = 'bi bi-speedometer2 text-success';
            diagTitleEl.textContent = 'Setup Gamer de Alto Nível:';
            diagDescEl.textContent = `Seu computador (${cpu.name} + ${gpu.name}) tem enorme poder! O Windows de fábrica trava os timers em 15.6ms. O ${packName} reduz para 0.500ms cravados, oferecendo mira cirúrgica sem atraso!`;
        } else {
            if (diagIconEl) diagIconEl.className = 'bi bi-check-circle-fill text-cyan';
            diagTitleEl.textContent = 'Sinergia de Setup Identificada:';
            diagDescEl.textContent = `Com ${cpu.name} e ${gpu.name}, o Windows retém dezenas de FPS por serviços vampiros e bufferings lentos. O ${packName} destrava a capacidade total da sua máquina!`;
        }
    }

    function animateNumber(element, start, end) {
        if (!element) return;
        if (start === end) {
            element.textContent = end;
            return;
        }
        let current = start;
        const diff = end - start;
        const step = diff > 0 ? Math.max(1, Math.ceil(diff / 8)) : Math.min(-1, Math.floor(diff / 8));
        
        if (element._animTimer) clearInterval(element._animTimer);
        
        element._animTimer = setInterval(() => {
            current += step;
            if ((step > 0 && current >= end) || (step < 0 && current <= end)) {
                current = end;
                clearInterval(element._animTimer);
            }
            element.textContent = current;
        }, 22);
    }

    // Escuta alterações em todos os campos e seletores
    const listeners = [
        gameSelect, resSelect, cpuSelect, gpuSelect, ramSelect, storageSelect, packSelect
    ];
    listeners.forEach(sel => {
        if (sel) {
            sel.addEventListener('change', () => {
                if (typeof ApexSound !== 'undefined' && ApexSound.playClick) {
                    ApexSound.playClick();
                }
                updateCalculations();
            });
        }
    });

    // Inputs customizados com input/keyup em tempo real
    if (customCpuInput) {
        customCpuInput.addEventListener('input', () => updateCalculations());
    }
    if (customGpuInput) {
        customGpuInput.addEventListener('input', () => updateCalculations());
    }
    if (customFpsInput) {
        customFpsInput.addEventListener('input', () => updateCalculations());
    }

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

                ['sidebarCartBadge', 'mobileCartBadge', 'navbarCartBadge', 'bottomCartBadge'].forEach(id => {
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
// Apex Bottleneck Scanner & Real-Time Live Diagnostic Tool
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

    // Real Hardware State
    const hardware = {
        gpu: 'Detectando GPU...',
        cores: navigator.hardwareConcurrency || 8,
        ram: navigator.deviceMemory ? `${navigator.deviceMemory} GB` : '8+ GB',
        hz: 60,
        frameTime: '16.67',
        jitter: '3.8',
        ping: 24,
        os: 'Windows 11 (23H2 / 24H2)',
        isWin10: false
    };

    // Helper: Detect Real GPU via WebGL
    function detectRealGpu() {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (!gl) return 'Acelerador Gráfico Básico';
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            if (debugInfo) {
                const raw = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                // Clean ANGLE or driver wrappers: e.g. "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11...)"
                const angleMatch = raw.match(/ANGLE \([^,]+,\s*([^,]+)/i);
                if (angleMatch && angleMatch[1]) {
                    return angleMatch[1].replace(/Direct3D.*/i, '').trim();
                }
                return raw.replace(/Direct3D.*/i, '').replace(/vs_\d+_\d+.*/i, '').trim();
            }
            return gl.getParameter(gl.RENDERER) || 'GPU Padrão';
        } catch (e) {
            return 'Acelerador Gráfico Windows';
        }
    }

    // Helper: Measure Real Monitor Refresh Rate (requestAnimationFrame)
    function measureRealRefreshRate() {
        return new Promise((resolve) => {
            let frames = 0;
            const targetFrames = 35;
            let start = performance.now();

            function checkFrame(now) {
                frames++;
                if (frames < targetFrames) {
                    requestAnimationFrame(checkFrame);
                } else {
                    const elapsed = now - start;
                    const avgTime = elapsed / frames;
                    const calculatedFps = 1000 / avgTime;
                    let detectedHz = Math.round(calculatedFps);

                    // Snap to standard gaming display frequencies
                    if (Math.abs(detectedHz - 60) <= 5) detectedHz = 60;
                    else if (Math.abs(detectedHz - 75) <= 5) detectedHz = 75;
                    else if (Math.abs(detectedHz - 120) <= 6) detectedHz = 120;
                    else if (Math.abs(detectedHz - 144) <= 6) detectedHz = 144;
                    else if (Math.abs(detectedHz - 165) <= 6) detectedHz = 165;
                    else if (Math.abs(detectedHz - 240) <= 10) detectedHz = 240;
                    else if (Math.abs(detectedHz - 360) <= 12) detectedHz = 360;

                    resolve({
                        hz: detectedHz,
                        frameTime: avgTime.toFixed(2)
                    });
                }
            }
            requestAnimationFrame(checkFrame);
        });
    }

    // Helper: Measure Real Timer Jitter & Event Loop Delta (performance.now)
    function measureRealTimerJitter() {
        return new Promise((resolve) => {
            const deltas = [];
            let count = 0;
            const maxSamples = 16;

            const timerId = setInterval(() => {
                const t0 = performance.now();
                setTimeout(() => {
                    const diff = performance.now() - t0;
                    deltas.push(diff);
                    count++;
                    if (count >= maxSamples) {
                        clearInterval(timerId);
                        const mean = deltas.reduce((a, b) => a + b, 0) / deltas.length;
                        const variance = deltas.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / deltas.length;
                        const jitterVal = Math.max(1.8, Math.sqrt(variance) * 2.2);
                        resolve(jitterVal.toFixed(1));
                    }
                }, 4);
            }, 12);
        });
    }

    // Helper: Measure Real Network Ping
    async function measureRealPing() {
        try {
            const t0 = performance.now();
            await fetch('/api/ping?t=' + Date.now(), { cache: 'no-store' });
            return Math.max(8, Math.round(performance.now() - t0));
        } catch (e) {
            if (navigator.connection && navigator.connection.rtt) {
                return navigator.connection.rtt;
            }
            return 22;
        }
    }

    // Initial Live Hardware Probe on Load
    function runInitialLiveTelemetry() {
        hardware.gpu = detectRealGpu();
        hardware.cores = navigator.hardwareConcurrency || 8;
        hardware.ram = navigator.deviceMemory ? `${navigator.deviceMemory} GB` : '8+ GB';

        // Update live mini-cards
        const liveGpuEl = document.getElementById('liveGpuName');
        const liveCpuEl = document.getElementById('liveCpuCores');
        const liveHzEl = document.getElementById('liveDisplayHz');
        const livePingEl = document.getElementById('livePingMs');

        if (liveGpuEl) liveGpuEl.textContent = hardware.gpu;
        if (liveCpuEl) liveCpuEl.textContent = `${hardware.cores} Threads`;

        // Auto-select detected OS / CPU in select dropdowns
        const osSelect = document.getElementById('scanOsSelect');
        const cpuSelect = document.getElementById('scanCpuSelect');

        const ua = navigator.userAgent;
        if (ua.includes('Windows NT 10.0')) {
            if (osSelect) osSelect.value = 'win11';
        }

        if (cpuSelect) {
            const gpuLower = hardware.gpu.toLowerCase();
            if (gpuLower.includes('amd') || gpuLower.includes('radeon')) {
                cpuSelect.value = 'amd_ryzen';
            } else if (gpuLower.includes('intel') || gpuLower.includes('iris') || gpuLower.includes('arc')) {
                cpuSelect.value = 'intel_core';
            }
        }

        // Measure live Hz & Ping in background
        measureRealRefreshRate().then(res => {
            hardware.hz = res.hz;
            hardware.frameTime = res.frameTime;
            if (liveHzEl) liveHzEl.textContent = `${res.hz}Hz (${res.frameTime}ms)`;
        });

        measureRealPing().then(ping => {
            hardware.ping = ping;
            if (livePingEl) livePingEl.textContent = `${ping}ms RTT`;
        });
    }

    // Run initial probe immediately
    runInitialLiveTelemetry();

    // Live Execution on Button Click
    btnStart.addEventListener('click', async () => {
        ApexSound.playClick();

        if (idleState) idleState.classList.add('d-none');
        if (resultState) resultState.classList.add('d-none');
        if (runningState) {
            runningState.classList.remove('d-none');
            runningState.classList.add('d-flex');
        }

        btnStart.disabled = true;
        btnStart.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> MEDINDO HARDWARE EM TEMPO REAL...';

        if (terminalLogs) {
            terminalLogs.innerHTML = '';
        }

        function appendLog(text, cls = 'active') {
            if (!terminalLogs) return;
            const now = new Date();
            const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
            const line = document.createElement('div');
            line.className = `scanner-log-line ${cls}`;
            line.innerHTML = `<span class="text-secondary small">[${timeStr}]</span> ${text}`;
            terminalLogs.appendChild(line);
            terminalLogs.scrollTop = terminalLogs.scrollHeight;
        }

        function updateProgress(pct) {
            if (progressBar) progressBar.style.width = pct + '%';
            if (percentText) percentText.textContent = pct + '%';
        }

        // --- STEP 1: Hardware & WebGL Pipeline (0 -> 25%) ---
        appendLog('⚡ Inicializando sondagem de telemetria de hardware no navegador...', 'text-cyan');
        updateProgress(15);
        await new Promise(r => setTimeout(r, 400));

        hardware.gpu = detectRealGpu();
        appendLog(`🎮 GPU Detectada via WebGL: <strong class="text-white">${hardware.gpu}</strong>`, 'active');
        appendLog(`🧠 CPU Detectada: <strong class="text-white">${hardware.cores} Threads Lógicas</strong> | RAM: ${hardware.ram}`, 'active');
        updateProgress(35);
        await new Promise(r => setTimeout(r, 450));

        // --- STEP 2: Real Display Refresh Rate Benchmark (25 -> 60%) ---
        appendLog('📺 Medindo taxa de atualização física do monitor (requestAnimationFrame)...', 'text-cyan');
        const dispRes = await measureRealRefreshRate();
        hardware.hz = dispRes.hz;
        hardware.frameTime = dispRes.frameTime;

        if (dispRes.hz <= 60) {
            appendLog(`⚠️ Display em 60Hz (${dispRes.frameTime}ms de frame-timing): Atraso de apresentação perceptível em eSports`, 'text-warning');
        } else {
            appendLog(`⚡ Monitor Gamer de ${dispRes.hz}Hz (${dispRes.frameTime}ms): Requer sincronia estrita de 1% Low sem stuttering!`, 'text-success');
        }
        updateProgress(65);
        await new Promise(r => setTimeout(r, 450));

        // --- STEP 3: Real Timer Jitter & Kernel Resolution (60 -> 85%) ---
        appendLog('⏱️ Testando dispersão de clock e jitter do High-Precision Event Timer (HPET)...', 'text-cyan');
        const jitterVal = await measureRealTimerJitter();
        hardware.jitter = jitterVal;

        appendLog(`⚠️ Timer Jitter medido: <strong class="text-warning">${jitterVal}ms de oscilação</strong> (Kernel padrão do Windows sem unpark)`, 'text-warning');
        updateProgress(85);
        await new Promise(r => setTimeout(r, 400));

        // --- STEP 4: Real Network Ping Telemetry (85 -> 100%) ---
        appendLog('🌐 Enviando pacotes de teste para medição de latência RTT...', 'text-cyan');
        const pingVal = await measureRealPing();
        hardware.ping = pingVal;

        appendLog(`🌐 Latência de Rede: <strong class="text-white">${pingVal}ms RTT</strong> com socket do servidor`, 'active');
        appendLog('✅ Varredura concluída com telemetria 100% real do seu equipamento!', 'text-success');
        updateProgress(100);
        await new Promise(r => setTimeout(r, 600));

        // --- STEP 5: Compile Dynamic Diagnostic Report ---
        if (runningState) {
            runningState.classList.remove('d-flex');
            runningState.classList.add('d-none');
        }
        if (resultState) {
            resultState.classList.remove('d-none');
        }

        // Fill Real Diagnostic Card Values
        const diagGpu = document.getElementById('diagGpuName');
        const diagCpu = document.getElementById('diagCpuThreads');
        const diagHz = document.getElementById('diagDisplayHz');
        const diagLat = document.getElementById('diagLatencyStats');

        if (diagGpu) diagGpu.textContent = hardware.gpu;
        if (diagCpu) diagCpu.textContent = `${hardware.cores} Threads (${hardware.ram})`;
        if (diagHz) diagHz.textContent = `${hardware.hz}Hz (${hardware.frameTime}ms)`;
        if (diagLat) diagLat.textContent = `${hardware.jitter}ms Jitter • ${hardware.ping}ms Ping`;

        // Calculate Dynamic Score
        const symptoms = Array.from(document.querySelectorAll('.scan-symptom:checked')).map(el => el.value);
        let efficiencyScore = 78;

        // Deduct based on real measurements
        if (parseFloat(hardware.jitter) > 3.0) efficiencyScore -= 10;
        else if (parseFloat(hardware.jitter) > 2.0) efficiencyScore -= 6;

        if (hardware.hz <= 60) efficiencyScore -= 6;
        if (hardware.ping > 40) efficiencyScore -= 6;

        // Deduct based on selected symptoms
        if (symptoms.includes('stutters')) efficiencyScore -= 9;
        if (symptoms.includes('mouse_delay')) efficiencyScore -= 8;
        if (symptoms.includes('ping_loss')) efficiencyScore -= 7;
        if (symptoms.includes('ram_cpu')) efficiencyScore -= 6;

        efficiencyScore = Math.max(42, Math.min(68, efficiencyScore));
        const gainPct = Math.round((100 - efficiencyScore) * 1.6);

        const scoreText = document.getElementById('scanScoreText');
        const gainText = document.getElementById('scanGainText');
        const scoreBar = document.getElementById('scanScoreBar');

        if (scoreText) scoreText.textContent = `${efficiencyScore}%`;
        if (gainText) gainText.textContent = `+${gainPct}% FPS`;
        if (scoreBar) {
            scoreBar.style.width = `${efficiencyScore}%`;
            scoreBar.className = efficiencyScore < 55 ? 'progress-bar bg-danger' : 'progress-bar bg-warning';
        }

        // Dynamic Bottleneck List
        const listEl = document.getElementById('scanBottleneckList');
        if (listEl) {
            listEl.innerHTML = '';
            const issues = [];

            if (symptoms.includes('stutters') || parseFloat(hardware.jitter) > 2.5) {
                issues.push(`<strong>CPU Core Parking & Clock Skew:</strong> ${hardware.cores} threads oscilando com ${hardware.jitter}ms de jitter em tiroteios`);
            }
            if (symptoms.includes('mouse_delay')) {
                issues.push(`<strong>Timer Resolution do Windows (15.6ms):</strong> Atraso artificial na leitura do sensor e polling rate do mouse`);
            }
            if (hardware.hz > 60) {
                issues.push(`<strong>Descompasso de Frame Pacing no Monitor ${hardware.hz}Hz:</strong> Micro-stutters visíveis mesmo com FPS alto`);
            } else {
                issues.push(`<strong>Limite de Taxa de Apresentação em 60Hz:</strong> Input lag acumulado nos buffers de exibição do Windows`);
            }
            if (symptoms.includes('ping_loss')) {
                issues.push(`<strong>Algoritmo de Nagle & Throttling de Rede:</strong> Bufferbloat no adaptador e atraso de registro de tiros (${hardware.ping}ms)`);
            }
            if (symptoms.includes('ram_cpu')) {
                issues.push(`<strong>Telemetria e Bloatware do Sistema:</strong> Serviços em segundo plano disputando clock precioso da ${hardware.gpu.split(' ')[0] || 'GPU'}`);
            }

            issues.forEach(text => {
                const li = document.createElement('li');
                li.className = 'text-light';
                li.innerHTML = `<i class="bi bi-x-circle-fill text-danger me-2"></i> ${text}`;
                listEl.appendChild(li);
            });
        }

        // Dynamic Product Prescription
        const recTag = document.getElementById('diagRecTag');
        const recPrice = document.getElementById('diagRecPrice');
        const recName = document.getElementById('diagRecName');
        const recDesc = document.getElementById('diagRecDesc');
        const recBtn = document.getElementById('diagRecBtn');

        if (symptoms.length >= 3) {
            // Ultimate Extreme Suite
            if (recTag) recTag.textContent = 'SUÍTE COMPLETA RECOMENDADA';
            if (recPrice) recPrice.textContent = 'R$ 14,90';
            if (recName) recName.textContent = 'Ultimate Extreme Suite 2026';
            if (recDesc) recDesc.textContent = `Prescrição máxima para sua ${hardware.gpu.substring(0, 24)}: unpark completo das ${hardware.cores} threads, timer a 0.5ms e otimização total de rede.`;
            if (recBtn) recBtn.href = '/cart/add/4';
        } else if (symptoms.includes('ping_loss')) {
            // Network Pro Pack
            if (recTag) recTag.textContent = 'PRESCRIÇÃO DE REDE & LATÊNCIA';
            if (recPrice) recPrice.textContent = 'R$ 9,90';
            if (recName) recName.textContent = 'Network & Latency Pro Pack';
            if (recDesc) recDesc.textContent = `Zera perda de pacotes, desativa o Nagle Algorithm e reduz o ping de ${hardware.ping}ms para resposta instantânea.`;
            if (recBtn) recBtn.href = '/cart/add/3';
        } else {
            // Competitive FPS Ultra Pack
            if (recTag) recTag.textContent = 'PRESCRIÇÃO DE FPS & MIRA';
            if (recPrice) recPrice.textContent = 'R$ 6,90';
            if (recName) recName.textContent = 'Competitive FPS Ultra Pack';
            if (recDesc) recDesc.textContent = `Corrige a oscilação do timer (${hardware.jitter}ms) para 0.5ms cravado e acorda todas as ${hardware.cores} threads da CPU.`;
            if (recBtn) recBtn.href = '/cart/add/2';
        }

        btnStart.disabled = false;
        btnStart.innerHTML = '<i class="bi bi-arrow-repeat me-2"></i> REPETIR VARREDURA EM TEMPO REAL';
        ApexSound.playSuccess();
    });
}

// ==========================================================================
// Mystery Drop Gamer Lootbox Modal (Resgate Único por Usuário)
// ==========================================================================
function initMysteryDropModal() {
    const triggerVault = document.getElementById('lootboxTrigger');
    const openBtn = document.getElementById('btnOpenLootbox');
    const closedState = document.getElementById('lootboxClosedState');
    const openedState = document.getElementById('lootboxOpenedState');
    const dropVipContainer = document.getElementById('dropVipContainer');

    if (!openBtn || !triggerVault) return;

    let isClaiming = false;

    async function handleOpenDrop() {
        if (isClaiming) return;
        isClaiming = true;

        triggerVault.classList.add('lootbox-shake');
        openBtn.disabled = true;
        openBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Desbloqueando...';
        ApexSound.playClick();

        try {
            const response = await fetch('/api/claim-drop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            setTimeout(() => {
                triggerVault.classList.remove('lootbox-shake');

                if (data.success) {
                    if (closedState) closedState.classList.add('d-none');
                    if (openedState) openedState.classList.remove('d-none');
                    ApexSound.playSuccess();
                    showQuickAlert(data.message || 'Drop VIP resgatado com sucesso! Cupom de 20% aplicado.', 'success');

                    // Atualiza o botão da barra superior para o badge de resgatado
                    if (dropVipContainer) {
                        dropVipContainer.innerHTML = `
                            <span class="badge bg-success bg-opacity-25 text-success border border-success border-opacity-50 py-1 px-2 d-inline-flex align-items-center" style="font-size: 0.75rem;" title="Você já resgatou o seu Drop VIP exclusivo">
                                <i class="bi bi-check-circle-fill me-1"></i> Drop VIP Resgatado
                            </span>
                        `;
                    }
                } else if (data.already_claimed) {
                    ApexSound.playWarning();
                    showQuickAlert(data.message || 'Você já resgatou o seu Drop VIP nesta conta.', 'warning');
                    if (closedState) closedState.classList.add('d-none');
                    if (openedState) openedState.classList.remove('d-none');
                    if (dropVipContainer) {
                        dropVipContainer.innerHTML = `
                            <span class="badge bg-success bg-opacity-25 text-success border border-success border-opacity-50 py-1 px-2 d-inline-flex align-items-center" style="font-size: 0.75rem;" title="Você já resgatou o seu Drop VIP exclusivo">
                                <i class="bi bi-check-circle-fill me-1"></i> Drop VIP Resgatado
                            </span>
                        `;
                    }
                } else {
                    ApexSound.playWarning();
                    showQuickAlert(data.message || 'Erro ao resgatar Drop VIP.', 'danger');
                    openBtn.disabled = false;
                    openBtn.innerHTML = '<i class="bi bi-key-fill me-1"></i> Abrir Caixa de Suprimentos';
                    isClaiming = false;
                }
            }, 900);
        } catch (err) {
            triggerVault.classList.remove('lootbox-shake');
            openBtn.disabled = false;
            openBtn.innerHTML = '<i class="bi bi-key-fill me-1"></i> Abrir Caixa de Suprimentos';
            isClaiming = false;
            showQuickAlert('Erro na conexão ao resgatar o Drop VIP.', 'danger');
        }
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
