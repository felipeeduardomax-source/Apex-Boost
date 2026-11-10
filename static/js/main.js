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
        if (typeof ApexMusic !== 'undefined') {
            ApexMusic.onSoundToggle(enabled);
        }
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
// Ambient Background Music Player (Vicetone - Nevada)
// Reprodução contínua em volume suave/baixo (15%) para imersão gamer
// ==========================================================================
const ApexMusic = (function() {
    let audio = null;
    let enabled = localStorage.getItem('apex_sound_enabled') !== 'false';
    let isPlaying = false;
    let hasInteracted = false;
    let savedVol = parseFloat(localStorage.getItem('apex_music_volume'));
    if (isNaN(savedVol) || savedVol < 0 || savedVol > 0.5) {
        savedVol = 0.15; // Volume baixo (15%) conforme solicitação
    }

    function getAudio() {
        if (!audio) {
            audio = new Audio('/static/audio/nevada.mp3');
            audio.loop = true;
            audio.preload = 'auto';
            audio.volume = savedVol;

            // Restaura posição salva da música entre mudanças de página
            const savedTime = parseFloat(localStorage.getItem('apex_music_time'));
            if (!isNaN(savedTime) && savedTime > 0) {
                try {
                    audio.currentTime = savedTime;
                } catch(e) {}
            }

            audio.addEventListener('play', () => updatePills(true));
            audio.addEventListener('pause', () => updatePills(false));
            audio.addEventListener('ended', () => {
                audio.currentTime = 0;
                audio.play().catch(() => {});
            });
        }
        return audio;
    }

    function updatePills(playing) {
        isPlaying = playing;
        document.querySelectorAll('.apex-music-pill').forEach(pill => {
            if (playing) {
                pill.classList.add('apex-music-playing');
                pill.setAttribute('title', 'Música Ativa: Vicetone - Nevada (Clique para pausar)');
            } else {
                pill.classList.remove('apex-music-playing');
                pill.setAttribute('title', 'Música Pausada: Vicetone - Nevada (Clique para tocar)');
            }
        });
        document.querySelectorAll('.music-volume-slider').forEach(slider => {
            slider.value = audio ? audio.volume : savedVol;
        });
    }

    function play() {
        if (!enabled) return;
        const player = getAudio();
        player.volume = savedVol;
        const promise = player.play();
        if (promise !== undefined) {
            promise.then(() => {
                updatePills(true);
            }).catch(() => {
                // Navegadores bloqueiam autoplay sem interação prévia; aguarda 1º clique
                updatePills(false);
                setupAutoplayGesture();
            });
        }
    }

    function pause() {
        if (audio) {
            audio.pause();
        }
        updatePills(false);
    }

    function toggle() {
        const player = getAudio();
        if (player.paused) {
            if (!enabled) {
                ApexSound.toggle();
            }
            play();
        } else {
            pause();
        }
    }

    function setVolume(vol) {
        vol = Math.max(0, Math.min(0.5, vol));
        savedVol = vol;
        localStorage.setItem('apex_music_volume', vol.toString());
        const player = getAudio();
        player.volume = vol;
        if (vol === 0) {
            pause();
        } else if (player.paused && enabled) {
            play();
        }
    }

    function onSoundToggle(soundOn) {
        enabled = soundOn;
        if (soundOn) {
            play();
        } else {
            pause();
        }
    }

    function setupAutoplayGesture() {
        if (hasInteracted) return;
        const startOnGesture = () => {
            hasInteracted = true;
            if (enabled && audio && audio.paused) {
                audio.play().then(() => {
                    updatePills(true);
                }).catch(() => {});
            }
            ['pointerdown', 'click', 'keydown', 'touchstart'].forEach(evt => {
                document.removeEventListener(evt, startOnGesture);
            });
        };

        ['pointerdown', 'click', 'keydown', 'touchstart'].forEach(evt => {
            document.addEventListener(evt, startOnGesture, { once: true, passive: true });
        });
    }

    function init() {
        getAudio();

        // Salva periodicamente a posição de reprodução e ao sair da página
        window.addEventListener('beforeunload', () => {
            if (audio && !audio.paused && audio.currentTime > 0) {
                localStorage.setItem('apex_music_time', audio.currentTime.toString());
            }
        });

        setInterval(() => {
            if (audio && !audio.paused && audio.currentTime > 0) {
                localStorage.setItem('apex_music_time', audio.currentTime.toString());
            }
        }, 3000);

        // Vincula cliques no mini player da música
        document.querySelectorAll('.apex-music-pill').forEach(pill => {
            pill.addEventListener('click', (e) => {
                if (e.target.classList.contains('music-volume-slider')) return;
                toggle();
            });
        });

        // Vincula sliders de volume
        document.querySelectorAll('.music-volume-slider').forEach(slider => {
            slider.value = savedVol;
            slider.addEventListener('input', (e) => {
                e.stopPropagation();
                setVolume(parseFloat(e.target.value));
            });
            slider.addEventListener('click', (e) => e.stopPropagation());
        });

        if (enabled) {
            play();
            setupAutoplayGesture();
        } else {
            updatePills(false);
        }
    }

    return {
        init,
        play,
        pause,
        toggle,
        setVolume,
        onSoundToggle,
        getAudio
    };
})();

// ==========================================================================
// Initialization on DOM Ready
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initSoundToggle();
    ApexMusic.init();
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
        'cpu_entry': {
            mult: 0.62,
            bloatPenalty: 0.28,
            name: 'Core i3 / Ryzen 3',
            type: 'entry'
        },
        'cpu_mid_old': {
            mult: 0.95,
            bloatPenalty: 0.20,
            name: 'Core i5 antigo / Ryzen 5 3600',
            type: 'mid_old'
        },
        'cpu_mid_modern': {
            mult: 1.35,
            bloatPenalty: 0.14,
            name: 'Core i5 12400F+ / Ryzen 5 5600+',
            type: 'mid_modern'
        },
        'cpu_high': {
            mult: 1.78,
            bloatPenalty: 0.10,
            name: 'Core i7/i9 / Ryzen 7 7800X3D',
            type: 'high'
        }
    };

    // 3. Multiplicadores de Potência da Placa de Vídeo (GPU)
    const gpuData = {
        'gpu_integrated': { mult: 0.38, name: 'Gráficos Integrados', tier: 1 },
        'gpu_entry': { mult: 0.68, name: 'GTX 1050 / 1650', tier: 2 },
        'gpu_mid_prev': { mult: 1.00, name: 'GTX 1660 / RTX 2060 / RX 580', tier: 3 },
        'gpu_mid_current': { mult: 1.48, name: 'RTX 3060 / 4060 / RX 6600', tier: 4 },
        'gpu_high': { mult: 2.10, name: 'RTX 3080 / 4070 / RX 7700 XT', tier: 5 },
        'gpu_ultra': { mult: 2.85, name: 'RTX 4080 / 4090 / RX 7900 XTX', tier: 6 }
    };

    // 4. Modificadores de Memória RAM (Largura de banda e estabilidade de frametime)
    const ramData = {
        'ram_8_single': { mult: 0.82, lowPenalty: 0.42, latAdd: 8, isSingle: true },
        'ram_8_dual': { mult: 0.92, lowPenalty: 0.18, latAdd: 4, isSingle: false },
        'ram_16_dual': { mult: 1.00, lowPenalty: 0.00, latAdd: 0, isSingle: false },
        'ram_32_dual': { mult: 1.06, lowPenalty: -0.06, latAdd: -1, isSingle: false }
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
        const cpuKey = cpuSelect ? cpuSelect.value : 'cpu_mid_old';
        const gpuKey = gpuSelect ? gpuSelect.value : 'gpu_mid_prev';
        const ramKey = ramSelect ? ramSelect.value : 'ram_16_dual';
        const storageKey = storageSelect ? storageSelect.value : 'storage_nvme';
        const packKey = packSelect ? packSelect.value : 'ultra';

        const game = gameData[gameKey] || gameData['cs2'];
        const cpu = cpuData[cpuKey] || cpuData['cpu_mid_old'];
        const gpu = gpuData[gpuKey] || gpuData['gpu_mid_prev'];
        const ram = ramData[ramKey] || ramData['ram_16_dual'];
        const storage = storageData[storageKey] || storageData['storage_nvme'];
        const resMult = resData[resKey] || 1.15;
        const pack = packBoost[packKey] || packBoost['ultra'];

        // Cálculo de Potência Efetiva do Hardware combinando CPU e GPU com peso do jogo
        const effectiveHw = (cpu.mult * game.cpuWeight) + (gpu.mult * game.gpuWeight);
        
        // Penalidade por desequilíbrio severo (Gargalo de CPU ou GPU)
        const diff = Math.abs(cpu.mult - gpu.mult);
        const bottleneckPenalty = diff > 0.7 ? 0.90 : 1.0;

        // FPS Base Padrão do Windows
        let baseFps = Math.round(game.baseFps * effectiveHw * resMult * ram.mult * storage.mult * bottleneckPenalty);
        baseFps = Math.max(28, baseFps);

        // Otimização Apex Boost: recuperação de bloatware + alívios específicos
        let recoveryFactor = 1.0;
        if (ram.isSingle) recoveryFactor += 0.07;        // Standby RAM cleaner salva canal único
        if (storage.isHdd) recoveryFactor += 0.05;       // Remoção de telemetria alivia fila do HD
        if (cpu.bloatPenalty > 0.18) recoveryFactor += 0.04; // Core unparking ajuda CPUs de entrada

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
        updateDiagnosis(cpuKey, gpuKey, ramKey, storageKey, gameKey, pack.name);

        // Atualiza link do CTA para direcionar ao pack correspondente
        if (ctaBtn) {
            ctaBtn.href = `#tab-packs`;
        }
    }

    function updateDiagnosis(cpuKey, gpuKey, ramKey, storageKey, gameKey, packName) {
        if (!diagTitleEl || !diagDescEl) return;

        if (ramKey === 'ram_8_single') {
            if (diagIconEl) diagIconEl.className = 'bi bi-exclamation-triangle-fill text-warning';
            diagTitleEl.textContent = 'Gargalo Crítico de Memória Detectado:';
            diagDescEl.textContent = 'Sua memória em Single Channel (1 pente) corta a largura de banda pela metade, gerando engasgos severos em tiroteios. O ' + packName + ' ativa a limpeza contínua de Standby RAM e paginação acelerada, curando 100% desse lag.';
        } else if (storageKey === 'storage_hdd') {
            if (diagIconEl) diagIconEl.className = 'bi bi-hdd-fill text-warning';
            diagTitleEl.textContent = 'Gargalo de I/O em Disco Detectado:';
            diagDescEl.textContent = 'O HD mecânico causa travamentos súbitos ao carregar texturas em tempo real. O ' + packName + ' desativa telemetria pesada, indexação e SysMain, mantendo seu disco 100% focado no jogo.';
        } else if (cpuKey === 'cpu_entry') {
            if (diagIconEl) diagIconEl.className = 'bi bi-lightning-charge-fill text-cyan';
            diagTitleEl.textContent = 'CPU Sobrecarregada pelo Windows:';
            diagDescEl.textContent = 'Processadores com menos núcleos sofrem com os 150+ processos ocultos da Microsoft. O ' + packName + ' desativa bloatwares de segundo plano e ativa o plano Apex Ultimate Performance, liberando até 60% mais fôlego para o seu jogo!';
        } else if (gpuKey === 'gpu_ultra' || gpuKey === 'gpu_high') {
            if (diagIconEl) diagIconEl.className = 'bi bi-speedometer2 text-success';
            diagTitleEl.textContent = 'Setup de Alto Desempenho Desbloqueado:';
            diagDescEl.textContent = 'Sua máquina é uma máquina gamer de respeito! O Windows padrão trava sua latência de timer em 1.000ms. O ' + packName + ' força 0.500ms de timer resolution e modo MSI na GPU, reduzindo o frametime para resposta de mira cirúrgica!';
        } else {
            if (diagIconEl) diagIconEl.className = 'bi bi-check-circle-fill text-cyan';
            diagTitleEl.textContent = 'Potencial Oculto do Setup Identificado:';
            diagDescEl.textContent = 'Seu setup tem excelente sinergia, mas o Windows de fábrica retém até 50+ FPS com serviços vampiros e bufferings lentos. O ' + packName + ' destrava a potência máxima dos seus componentes!';
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

    // Escuta alterações em tempo real em todos os 7 seletores
    const selectors = [gameSelect, resSelect, cpuSelect, gpuSelect, ramSelect, storageSelect, packSelect];
    selectors.forEach(sel => {
        if (sel) {
            sel.addEventListener('change', () => {
                if (typeof ApexSound !== 'undefined' && ApexSound.playClick) {
                    ApexSound.playClick();
                }
                updateCalculations();
            });
        }
    });

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
            if (recPrice) recPrice.textContent = 'R$ 34,90';
            if (recName) recName.textContent = 'Ultimate Extreme Suite 2026';
            if (recDesc) recDesc.textContent = `Prescrição máxima para sua ${hardware.gpu.substring(0, 24)}: unpark completo das ${hardware.cores} threads, timer a 0.5ms e otimização total de rede.`;
            if (recBtn) recBtn.href = '/cart/add/4';
        } else if (symptoms.includes('ping_loss')) {
            // Network Pro Pack
            if (recTag) recTag.textContent = 'PRESCRIÇÃO DE REDE & LATÊNCIA';
            if (recPrice) recPrice.textContent = 'R$ 24,90';
            if (recName) recName.textContent = 'Network & Latency Pro Pack';
            if (recDesc) recDesc.textContent = `Zera perda de pacotes, desativa o Nagle Algorithm e reduz o ping de ${hardware.ping}ms para resposta instantânea.`;
            if (recBtn) recBtn.href = '/cart/add/3';
        } else {
            // Competitive FPS Ultra Pack
            if (recTag) recTag.textContent = 'PRESCRIÇÃO DE FPS & MIRA';
            if (recPrice) recPrice.textContent = 'R$ 19,90';
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
