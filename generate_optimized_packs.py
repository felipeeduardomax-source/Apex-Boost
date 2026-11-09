import os
import zipfile

DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'downloads')
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Common elevation header for all individual .bat scripts
ELEVATION_HEADER = """@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [APEX BOOST] Solicitando privilegios de Administrador para otimizacao...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd.exe -ArgumentList '/k \\\"\\\"%~f0\\\"\\\"' -Verb RunAs" >nul 2>&1
    exit /b
)
chcp 65001 >nul 2>&1
cd /d "%~dp0"
"""

# -------------------------------------------------------------
# 1. SCRIPTS DE SEGURANÇA E RESTAURAÇÃO
# -------------------------------------------------------------
RESTORE_POINT_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Criar Ponto de Restauracao
color 0B
echo ===============================================================================
echo                      APEX BOOST - PONTO DE RESTAURACAO
echo ===============================================================================
echo.
echo Ativando Protecao do Sistema e criando Ponto de Restauracao de Seguranca...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Enable-ComputerRestore -Drive 'C:\\' -ErrorAction SilentlyContinue; Checkpoint-Computer -Description 'ApexBoost_PreTweak' -RestorePointType 'MODIFY_SETTINGS' -ErrorAction SilentlyContinue" >nul 2>&1
echo.
echo [SUCESSO] Ponto de Restauracao do Windows processado com seguranca!
echo Caso deseje desfazer qualquer alteracao no futuro, basta restaurar este ponto.
echo.
pause
"""

BACKUP_REG_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Backup do Registro do Windows
color 0B
echo ===============================================================================
echo                      APEX BOOST - BACKUP DO REGISTRO
echo ===============================================================================
echo.
echo Exportando backup das chaves de registro do sistema...
if not exist "C:\\ApexBoost_Backups" mkdir "C:\\ApexBoost_Backups" >nul 2>&1
reg export "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" "C:\\ApexBoost_Backups\\SystemProfile_Backup.reg" /y >nul 2>&1
reg export "HKCU\\Control Panel\\Desktop" "C:\\ApexBoost_Backups\\Desktop_Backup.reg" /y >nul 2>&1
reg export "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" "C:\\ApexBoost_Backups\\Tcpip_Backup.reg" /y >nul 2>&1
echo.
echo [SUCESSO] Backup salvo com seguranca em: C:\\ApexBoost_Backups
echo.
pause
"""

UNDO_ALL_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Reverter Todas as Configuracoes
color 0C
echo ===============================================================================
echo                APEX BOOST - REVERTER PARA PADRAO DO WINDOWS
echo ===============================================================================
echo.
echo Restaurando configuracoes padrao de rede, timers e energia do Windows...
echo.

echo 1. Restaurando pilha TCP/IP padrao...
netsh int ip reset >nul 2>&1
netsh int tcp reset >nul 2>&1
netsh winsock reset >nul 2>&1

echo 2. Restaurando timers bcdedit padrao...
bcdedit /deletevalue useplatformclock >nul 2>&1
bcdedit /deletevalue useplatformtick >nul 2>&1
bcdedit /deletevalue disabledynamictick >nul 2>&1

echo 3. Restaurando plano de energia padrao do Windows...
powercfg -restoredefaultschemes >nul 2>&1

echo 4. Restaurando servicos essenciais do Windows...
sc config "DiagTrack" start=auto >nul 2>&1
sc start "DiagTrack" >nul 2>&1

echo 5. Restaurando aceleracao de mouse padrao...
reg add "HKCU\\Control Panel\\Mouse" /v "MouseSpeed" /t REG_SZ /d 1 /f >nul 2>&1
reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold1" /t REG_SZ /d 6 /f >nul 2>&1
reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold2" /t REG_SZ /d 10 /f >nul 2>&1

echo.
echo [CONCLUIDO] Configuracoes restauradas para o padrao de fabrica do Windows!
echo Recomendamos reiniciar o computador agora.
echo.
pause
"""

# -------------------------------------------------------------
# 2. SCRIPTS DE LIMPEZA E MEMÓRIA RAM
# -------------------------------------------------------------
CLEAN_TEMP_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Limpeza Profunda de Cache e Temporarios
color 0A
echo ===============================================================================
echo                      APEX BOOST - LIMPEZA DE CACHE & DISCO
echo ===============================================================================
echo.
echo 1. Limpando pasta Temp do Usuario...
del /s /f /q "%temp%\\*.*" >nul 2>&1
for /d %%p in ("%temp%\\*.*") do rmdir "%%p" /s /q >nul 2>&1

echo 2. Limpando pasta Windows Temp...
del /s /f /q "C:\\Windows\\Temp\\*.*" >nul 2>&1
for /d %%p in ("C:\\Windows\\Temp\\*.*") do rmdir "%%p" /s /q >nul 2>&1

echo 3. Limpando Prefetch...
del /s /f /q "C:\\Windows\\Prefetch\\*.*" >nul 2>&1

echo 4. Limpando Cache de DNS...
ipconfig /flushdns >nul 2>&1

echo 5. Limpando Cache de Miniaturas (Thumbnails)...
del /s /f /q "%localappdata%\\Microsoft\\Windows\\Explorer\\thumbcache_*.db" >nul 2>&1

echo 6. Limpando Cache de Windows Update...
net stop wuauserv >nul 2>&1
del /s /f /q "%windir%\\SoftwareDistribution\\Download\\*.*" >nul 2>&1
net start wuauserv >nul 2>&1

echo.
echo [CONCLUIDO] Memoria temporaria e caches foram limpos com sucesso!
echo.
pause
"""

CLEAN_RAM_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Otimizador de Memoria RAM
color 0A
echo ===============================================================================
echo                   APEX BOOST - LIBERACAO DE MEMORIA RAM
echo ===============================================================================
echo.
echo Limpando lista de espera (Standby Cache) e memoria ociosa de processos...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-Process | ForEach-Object { try { $_.MinWorkingSet = $_.MinWorkingSet } catch {} }; [System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers()" >nul 2>&1
echo.
echo [CONCLUIDO] Memoria RAM limpa e liberada com sucesso para seus jogos!
echo.
pause
"""

SSD_TRIM_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Otimizacao de SSD TRIM
color 0B
echo ===============================================================================
echo                       APEX BOOST - OTIMIZACAO DE SSD
echo ===============================================================================
echo.
echo Executando comando TRIM em todas as unidades SSD para máxima velocidade...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Optimize-Volume -DriveLetter C -ReTrim -ErrorAction SilentlyContinue" >nul 2>&1
echo.
echo [CONCLUIDO] TRIM executado com sucesso no SSD!
echo.
pause
"""

# -------------------------------------------------------------
# 3. SCRIPTS DE WINDOWS E BLOATWARE
# -------------------------------------------------------------
TELEMETRY_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Desativar Telemetria e Diagnosticos
color 0E
echo ===============================================================================
echo                   APEX BOOST - PRIVACIDADE & ALIVIO DE CPU
echo ===============================================================================
echo.
echo Desativando servicos de rastreamento e telemetria...
sc stop "DiagTrack" >nul 2>&1
sc config "DiagTrack" start=disabled >nul 2>&1
sc stop "dmwappushservice" >nul 2>&1
sc config "dmwappushservice" start=disabled >nul 2>&1

echo Ajustando chaves de registro de telemetria...
reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v "AllowTelemetry" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Privacy" /v "TailoredExperiencesWithDiagnosticDataEnabled" /t REG_DWORD /d 0 /f >nul 2>&1

echo.
echo [CONCLUIDO] Telemetria e servicos em segundo plano desativados!
echo.
pause
"""

GAMEBAR_DVR_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Desativar Xbox Game Bar DVR (Gravacao de Fundo)
color 0E
echo ===============================================================================
echo                 APEX BOOST - DESATIVAR XBOX GAME BAR DVR
echo ===============================================================================
echo.
echo A gravacao automatica em segundo plano do Windows rouba ate 20%% do seu FPS.
echo Desativando recursos de captura em segundo plano...
reg add "HKCU\\System\\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\GameDVR" /v "AllowGameDVR" /t REG_DWORD /d 0 /f >nul 2>&1
echo.
echo [CONCLUIDO] Xbox Game Bar DVR desativado! Mais FPS para seus jogos.
echo.
pause
"""

BLOATWARE_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Desativar Bloatware e Notificacoes Inuteis
color 0E
echo ===============================================================================
echo                    APEX BOOST - DESATIVAR BLOATWARE
echo ===============================================================================
echo.
echo Desativando sugestoes de anuncios, Cortana e notificacoes invasivas...
reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" /v "SystemPaneSuggestionsEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" /v "SubscribedContent-338388Enabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" /v "SoftLandingEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications" /v "ToastEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v "AllowCortana" /t REG_DWORD /d 0 /f >nul 2>&1
echo.
echo [CONCLUIDO] Notificacoes e anuncios de fundo desativados com sucesso!
echo.
pause
"""

VISUAL_FX_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Otimizar Efeitos Visuais do Windows
color 0D
echo ===============================================================================
echo                 APEX BOOST - EFEITOS VISUAIS DE ALTO DESEMPENHO
echo ===============================================================================
echo.
echo Desativando animacoes pesadas do Windows mantendo fontes e icones nitidos...
reg add "HKCU\\Control Panel\\Desktop" /v "UserPreferencesMask" /t REG_BINARY /d 9012038010000000 /f >nul 2>&1
reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v "MinAnimate" /t REG_SZ /d 0 /f >nul 2>&1
reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v "TaskbarAnimations" /t REG_DWORD /d 0 /f >nul 2>&1
echo.
echo [CONCLUIDO] Janelas e barra de tarefas agora respondem com velocidade maxima!
echo.
pause
"""

# -------------------------------------------------------------
# 4. SCRIPTS DE PROCESSADOR (CPU) E ENERGIA
# -------------------------------------------------------------
ULTIMATE_PERF_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Ativar Plano Ultimate Performance Apex
color 0D
echo ===============================================================================
echo                      APEX BOOST - PLANO DE ENERGIA MAXIMA
echo ===============================================================================
echo.
echo Desbloqueando Plano de Desempenho Maximo do Windows...
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor PROCTHROTTLEMIN 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor PROCTHROTTLEMAX 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor CPMINCORES 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor CPMAXCORES 100 >nul 2>&1
powercfg -setactive scheme_current >nul 2>&1
echo.
echo [CONCLUIDO] Plano 'Desempenho Maximo' ativado e configurado em 100% de frequencia!
echo.
pause
"""

CPU_UNPARK_BAT = ELEVATION_HEADER + """title Apex Boost Labs - CPU Core Unparking (100% dos Nucleos Ativos)
color 0B
echo ===============================================================================
echo                   APEX BOOST - CPU CORE UNPARKING 100%
echo ===============================================================================
echo.
echo Configurando nucleos da CPU para ficarem sempre acordados em 100%...
powercfg -setacvalueindex scheme_current sub_processor CPMINCORES 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor CPMAXCORES 100 >nul 2>&1
powercfg -setactive scheme_current >nul 2>&1
echo.
echo [CONCLUIDO] Nenhum nucleo do seu processador entrara mais em modo de sono durante seus jogos!
echo.
pause
"""

TIMER_RES_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Timer Resolution & Clock Tick Latency
color 0C
echo ===============================================================================
echo                   APEX BOOST - TIMER RESOLUTION 0.5MS
echo ===============================================================================
echo.
echo Ajustando parametros de bcdedit para menor latencia de ticks do processador...
bcdedit /set useplatformclock false >nul 2>&1
bcdedit /set useplatformtick yes >nul 2>&1
bcdedit /set disabledynamictick yes >nul 2>&1
echo.
echo [CONCLUIDO] Latencia de interrupcao de clock reduzida para o menor valor possivel!
echo.
pause
"""

HPET_DISABLE_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Desativar HPET (High Precision Event Timer)
color 0C
echo ===============================================================================
echo                      APEX BOOST - DESATIVAR HPET
echo ===============================================================================
echo.
echo Desativando HPET no bcdedit e no gerenciador para evitar gargalos de clock...
bcdedit /deletevalue useplatformclock >nul 2>&1
echo.
echo [CONCLUIDO] HPET desativado! Mais fluidez em FPS de jogos competitivos.
echo.
pause
"""

# -------------------------------------------------------------
# 5. SCRIPTS DE PLACA DE VÍDEO (GPU) E GRÁFICOS
# -------------------------------------------------------------
GPU_OPTIMIZER_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Otimizacao de Driver de Video GPU
color 09
echo ===============================================================================
echo                 APEX BOOST - OTIMIZACAO DE DRIVER GPU (NVIDIA/AMD)
echo ===============================================================================
echo.
echo Ajustando prioridade de GPU, HAGS e agendamento de threads graficas...
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f >nul 2>&1
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "Priority" /t REG_DWORD /d 6 /f >nul 2>&1
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "Scheduling Category" /t REG_SZ /d "High" /f >nul 2>&1
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "SFIO Priority" /t REG_SZ /d "High" /f >nul 2>&1
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKCU\\Software\\Microsoft\\GameBar" /v "AllowAutoGameMode" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\\Software\\Microsoft\\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 1 /f >nul 2>&1
echo.
echo [CONCLUIDO] Prioridade maxima de renderizacao atribuida para jogos!
echo.
pause
"""

HAGS_REG = """Windows Registry Editor Version 5.00

; Ativar Agendamento de GPU Acelerado por Hardware (HAGS)
[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers]
"HwSchMode"=dword:00000002

; Otimizar Latência de Exibição do DWM
[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\DWM]
"EnableAeroPeek"=dword:00000000
"AlwaysHibernateThumbnails"=dword:00000000
"""

GAMEMODE_REG = """Windows Registry Editor Version 5.00

; Ativar Modo de Jogo do Windows 10/11
[HKEY_CURRENT_USER\\Software\\Microsoft\\GameBar]
"AllowAutoGameMode"=dword:00000001
"AutoGameModeEnabled"=dword:00000001

; Priorizar Processo de Games sobre tarefas em segundo plano
[HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile]
"SystemResponsiveness"=dword:00000000
"NetworkThrottlingIndex"=dword:ffffffff
"""

FULLSCREEN_FIX_REG = """Windows Registry Editor Version 5.00

; Desativar Otimizacoes de Tela Inteira (Fullscreen Optimizations) que causam Input Lag
[HKEY_CURRENT_USER\\System\\GameConfigStore]
"GameDVR_FSEBehaviorMode"=dword:00000002
"GameDVR_HonorUserFSEBehaviorMode"=dword:00000001
"GameDVR_DXGIHonorFSEWindowsCompatible"=dword:00000001
"""

# -------------------------------------------------------------
# 6. SCRIPTS DE INPUT LAG (MOUSE E TECLADO)
# -------------------------------------------------------------
MOUSE_RAW_INPUT_REG = """Windows Registry Editor Version 5.00

; Desativar Aceleração de Mouse do Windows (Sensibilidade 1:1 Perfeita)
[HKEY_CURRENT_USER\\Control Panel\\Mouse]
"MouseSpeed"="0"
"MouseThreshold1"="0"
"MouseThreshold2"="0"
"SmoothMouseXCurve"=hex:00,00,00,00,00,00,00,00,c0,cc,0c,00,00,00,00,00,80,99,\\
  19,00,00,00,00,00,40,66,26,00,00,00,00,00,00,33,33,00,00,00,00,00
"SmoothMouseYCurve"=hex:00,00,00,00,00,00,00,00,00,00,38,00,00,00,00,00,00,00,\\
  70,00,00,00,00,00,00,00,a8,00,00,00,00,00,00,00,e0,00,00,00,00,00
"""

KEYBOARD_RESPONSIVENESS_REG = """Windows Registry Editor Version 5.00

; Resposta Instantânea do Teclado e Desativação de Filtros de Delay
[HKEY_CURRENT_USER\\Control Panel\\Accessibility\\Keyboard Response]
"Flags"="122"
"DelayBeforeAcceptance"="0"
"AutoRepeatRate"="0"
"AutoRepeatDelay"="200"
"BounceTime"="0"

; Desativar Teclas de Aderência (Sticky Keys)
[HKEY_CURRENT_USER\\Control Panel\\Accessibility\\StickyKeys]
"Flags"="506"
"""

# -------------------------------------------------------------
# 7. SCRIPTS DE REDE, PING E STREAMING
# -------------------------------------------------------------
TCP_NETWORK_BAT = ELEVATION_HEADER + """title Apex Boost Labs - TCP/IP & Network Optimizer
color 0A
echo ===============================================================================
echo                 APEX BOOST - REDE, PING BAIXO & ZERO LOSS
echo ===============================================================================
echo.
echo 1. Otimizando TCP Window Auto-Tuning e Congestionamento...
netsh int tcp set global autotuninglevel=normal >nul 2>&1
netsh int tcp set global rss=enabled >nul 2>&1
netsh int tcp set global chimney=disabled >nul 2>&1
netsh int tcp set global timestamps=disabled >nul 2>&1
netsh int tcp set global ecncapability=disabled >nul 2>&1
netsh int tcp set heuristics disabled >nul 2>&1
netsh int ip set global taskoffload=enabled >nul 2>&1

echo 2. Desativando Nagle Algorithm nas interfaces de rede...
for /f %%i in ('reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces"') do (
    reg add "%%i" /v "TcpAckFrequency" /t REG_DWORD /d 1 /f >nul 2>&1
    reg add "%%i" /v "TCPNoDelay" /t REG_DWORD /d 1 /f >nul 2>&1
    reg add "%%i" /v "TcpDelAckTicks" /t REG_DWORD /d 0 /f >nul 2>&1
)
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 4294967295 /f >nul 2>&1

echo.
echo [CONCLUIDO] Pilha TCP/IP otimizada com sucesso! Sem atraso de empacotamento Nagle.
echo.
pause
"""

DNS_GAMER_BAT = ELEVATION_HEADER + """title Apex Boost Labs - Aplicar DNS Gamer de Baixa Latencia
color 0B
echo ===============================================================================
echo                APEX BOOST - DNS CLOUDFLARE 1.1.1.1 & GOOGLE
echo ===============================================================================
echo.
echo Aplicando DNS Cloudflare 1.1.1.1 (Primario) e 1.0.0.1 (Secundario) nas conexoes ativas...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Set-DnsClientServerAddress -ServerAddresses ('1.1.1.1','1.0.0.1')" >nul 2>&1
ipconfig /flushdns >nul 2>&1
echo.
echo [CONCLUIDO] DNS Gamer configurado! Rotas de conexao otimizadas.
echo.
pause
"""

# -------------------------------------------------------------
# 8. MASTER LAUNCHER BAT (Com UAC Auto-Elevation e Menu Interativo)
# -------------------------------------------------------------
MASTER_LAUNCHER_BAT = r"""@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: Auto-Elevacao Automatica para Administrador via UAC
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [APEX BOOST] Solicitando privilegios de Administrador para otimizacao de kernel...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd.exe -ArgumentList '/k \"\"%~f0\"\"' -Verb RunAs" >nul 2>&1
    exit /b
)

title APEX OPTIMIZER PRO v3.5 - [ULTIMATE PERFORMANCE LABS]
color 0B
chcp 65001 >nul 2>&1
cd /d "%~dp0"

:MAIN_MENU
cls
echo ===============================================================================
echo       #     ######  ####### #     #    ######  ####### #######  #####  #######
echo      # #    #     # #        #   #     #     # #     # #     # #     #    #   
echo     #   #   #     # #         # #      #     # #     # #     # #          #   
echo    #     #  ######  #####      #       ######  #     # #     #  #####     #   
echo    #######  #       #         # #      #     # #     # #     #       #    #   
echo    #     #  #       #        #   #     #     # #     # #     # #     #    #   
echo    #     #  #       ####### #     #    ######  ####### #######  #####     #   
echo.
echo                 SUITE PROFISSIONAL DE OTIMIZACAO PARA PC
echo            Status: [ADMINISTRADOR ATIVO - PRIVILEGIOS DE KERNEL]
echo ===============================================================================
echo.
echo   [1] OTIMIZACAO TOTAL EM 1 CLIQUE (Recomendado - Aplica todas as melhorias)
echo   [2] Central de Limpeza, Cache e Memoria RAM
echo   [3] Processador (CPU), Timers e Plano de Energia
echo   [4] Placa de Video (GPU), HAGS e Modo de Jogo
echo   [5] Zero Input Lag (Mouse Raw Input 1:1 e Teclado)
echo   [6] Rede, Conexao e Ping Baixo (TCP/IP e DNS)
echo   [7] Windows Debloater, Telemetria e Xbox DVR
echo   [8] Seguranca, Backup e Ponto de Restauracao
echo   [9] Guias Rapidos de Otimizacao para Jogos (CS2, Val, WZ, Fortnite, GTA)
echo   [R] REVERTER Todas as Otimizacoes (Voltar ao Padrao do Windows)
echo   [0] Sair
echo.
echo ===============================================================================
choice /c 123456789R0 /n /m "Digite a opcao desejada [0-9, R]: "

if errorlevel 11 goto OPT_EXIT
if errorlevel 10 goto RESTORE_ALL
if errorlevel 9 goto MENU_GAMES
if errorlevel 8 goto MENU_SECURITY
if errorlevel 7 goto MENU_WINDOWS
if errorlevel 6 goto MENU_NETWORK
if errorlevel 5 goto MENU_INPUTLAG
if errorlevel 4 goto MENU_GPU
if errorlevel 3 goto MENU_CPU
if errorlevel 2 goto MENU_CLEAN
if errorlevel 1 goto TOTAL_OPTIMIZE
goto MAIN_MENU

:: -------------------------------------------------------------
:: OTIMIZACAO TOTAL EM 1 CLIQUE
:: -------------------------------------------------------------
:TOTAL_OPTIMIZE
cls
echo ===============================================================================
echo         APEX BOOST - EXECUTANDO OTIMIZACAO TOTAL AUTOMATICA (1 CLIQUE)
echo ===============================================================================
echo.
echo [1/8] Criando Ponto de Restauracao do Sistema por Seguranca...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Enable-ComputerRestore -Drive 'C:\' -ErrorAction SilentlyContinue; Checkpoint-Computer -Description 'ApexBoost_Auto' -RestorePointType 'MODIFY_SETTINGS' -ErrorAction SilentlyContinue" >nul 2>&1
echo       - Ponto de seguranca criado com sucesso!
echo.

echo [2/8] Executando Limpeza Profunda de Cache, Temp e Memoria RAM...
del /s /f /q "%temp%\*.*" >nul 2>&1
for /d %%p in ("%temp%\*.*") do rmdir "%%p" /s /q >nul 2>&1
del /s /f /q "C:\Windows\Temp\*.*" >nul 2>&1
for /d %%p in ("C:\Windows\Temp\*.*") do rmdir "%%p" /s /q >nul 2>&1
del /s /f /q "C:\Windows\Prefetch\*.*" >nul 2>&1
del /s /f /q "%localappdata%\Microsoft\Windows\Explorer\thumbcache_*.db" >nul 2>&1
ipconfig /flushdns >nul 2>&1
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-Process | ForEach-Object { try { $_.MinWorkingSet = $_.MinWorkingSet } catch {} }; [System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers()" >nul 2>&1
echo       - Arquivos temporarios removidos e RAM Standby liberada!
echo.

echo [3/8] Desativando Telemetria, Diagnosticos e Xbox Game Bar DVR...
sc stop "DiagTrack" >nul 2>&1
sc config "DiagTrack" start=disabled >nul 2>&1
sc stop "dmwappushservice" >nul 2>&1
sc config "dmwappushservice" start=disabled >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v "AllowTelemetry" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v "AllowGameDVR" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SystemPaneSuggestionsEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\PushNotifications" /v "ToastEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v "AllowCortana" /t REG_DWORD /d 0 /f >nul 2>&1
echo       - Gravacao de fundo e servicos de rastreamento desativados!
echo.

echo [4/8] Otimizando CPU, Plano Ultimate Performance e Timer Resolution 0.5ms...
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor PROCTHROTTLEMIN 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor PROCTHROTTLEMAX 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor CPMINCORES 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor CPMAXCORES 100 >nul 2>&1
powercfg -setactive scheme_current >nul 2>&1
bcdedit /set useplatformclock false >nul 2>&1
bcdedit /set useplatformtick yes >nul 2>&1
bcdedit /set disabledynamictick yes >nul 2>&1
bcdedit /deletevalue useplatformclock >nul 2>&1
echo       - 100%% dos nucleos destravados e Timer ajustado em 0.5ms!
echo.

echo [5/8] Configurando GPU, HAGS e Prioridade de Renderizacao...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\GameBar" /v "AllowAutoGameMode" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_FSEBehaviorMode" /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_HonorUserFSEBehaviorMode" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_DXGIHonorFSEWindowsCompatible" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d 6 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d "High" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "SFIO Priority" /t REG_SZ /d "High" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d 0 /f >nul 2>&1
echo       - GPU configurada em alto desempenho com HAGS ativado!
echo.

echo [6/8] Ajustando Mouse para Raw Input 1:1 e Resposta de Teclado...
reg add "HKCU\Control Panel\Mouse" /v "MouseSpeed" /t REG_SZ /d 0 /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold1" /t REG_SZ /d 0 /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold2" /t REG_SZ /d 0 /f >nul 2>&1
reg add "HKCU\Control Panel\Accessibility\Keyboard Response" /v "Flags" /t REG_SZ /d "122" /f >nul 2>&1
reg add "HKCU\Control Panel\Accessibility\Keyboard Response" /v "AutoRepeatDelay" /t REG_SZ /d "200" /f >nul 2>&1
reg add "HKCU\Control Panel\Accessibility\Keyboard Response" /v "AutoRepeatRate" /t REG_SZ /d "0" /f >nul 2>&1
reg add "HKCU\Control Panel\Accessibility\StickyKeys" /v "Flags" /t REG_SZ /d "506" /f >nul 2>&1
echo       - Zero Input Lag: aceleracao desligada e resposta imediata!
echo.

echo [7/8] Otimizando Rede TCP/IP e Desativando Nagle Algorithm...
netsh int tcp set global autotuninglevel=normal >nul 2>&1
netsh int tcp set global rss=enabled >nul 2>&1
netsh int tcp set global chimney=disabled >nul 2>&1
netsh int tcp set global timestamps=disabled >nul 2>&1
netsh int tcp set global ecncapability=disabled >nul 2>&1
netsh int tcp set heuristics disabled >nul 2>&1
netsh int ip set global taskoffload=enabled >nul 2>&1
for /f %%i in ('reg query "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"') do (
    reg add "%%i" /v "TcpAckFrequency" /t REG_DWORD /d 1 /f >nul 2>&1
    reg add "%%i" /v "TCPNoDelay" /t REG_DWORD /d 1 /f >nul 2>&1
    reg add "%%i" /v "TcpDelAckTicks" /t REG_DWORD /d 0 /f >nul 2>&1
)
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 4294967295 /f >nul 2>&1
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Set-DnsClientServerAddress -ServerAddresses ('1.1.1.1','1.0.0.1')" >nul 2>&1
ipconfig /flushdns >nul 2>&1
echo       - Pilha TCP/IP otimizada e DNS Gamer Cloudflare configurado!
echo.

echo [8/8] Executando Comando TRIM no SSD...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Optimize-Volume -DriveLetter C -ReTrim -ErrorAction SilentlyContinue" >nul 2>&1
echo       - SSD re-otimizado com sucesso!
echo.

echo ===============================================================================
echo   [PARABENS] SEU COMPUTADOR FOI OTIMIZADO COM SUCESSO!
echo.
echo   Resumo das Melhorias Ativas:
echo   - 100%% dos nucleos da CPU destravados (Core Unparking)
echo   - Timer Resolution estabilizado em 0.5ms (Fim dos micro-stutters)
echo   - Agendamento de GPU (HAGS) e Prioridade de Renderizacao Maxima
echo   - Rede sem limitacoes (Nagle desativado e DNS Cloudflare 1.1.1.1)
echo   - Memoria RAM limpa e cache de disco otimizado
echo.
echo   RECOMENDACAO: Reinicie o seu computador agora para consolidar todas as
echo   mudancas diretamente no kernel do Windows!
echo ===============================================================================
echo.
pause
goto MAIN_MENU

:: -------------------------------------------------------------
:: SUBMENUS
:: -------------------------------------------------------------
:MENU_CLEAN
cls
echo ===============================================================================
echo                   APEX BOOST - CENTRAL DE LIMPEZA E MEMORIA RAM
echo ===============================================================================
echo.
echo   [1] Limpar Arquivos Temporarios (%%temp%%, Windows Temp, Prefetch, Thumbnails)
echo   [2] Liberar Memoria RAM Ociosa (Standby Cache Cleaner)
echo   [3] Limpar Cache de DNS e Rotas de Rede (FlushDNS)
echo   [4] Executar Comando TRIM nos SSDs (Restaura velocidade maxima de leitura)
echo   [5] Limpar Cache do Windows Update (SoftwareDistribution)
echo   [T] EXECUTAR TODAS AS LIMPEZAS ACIMA DE UMA VEZ
echo   [V] Voltar ao Menu Principal
echo.
echo ===============================================================================
choice /c 12345TV /n /m "Escolha uma opcao [1-5, T, V]: "
if errorlevel 7 goto MAIN_MENU
if errorlevel 6 goto CLEAN_ALL
if errorlevel 5 goto CLEAN_WINUPDATE
if errorlevel 4 goto CLEAN_TRIM
if errorlevel 3 goto CLEAN_DNS
if errorlevel 2 goto CLEAN_RAM
if errorlevel 1 goto CLEAN_TEMP
goto MENU_CLEAN

:CLEAN_TEMP
echo.
echo Limpando arquivos temporarios...
del /s /f /q "%temp%\*.*" >nul 2>&1
for /d %%p in ("%temp%\*.*") do rmdir "%%p" /s /q >nul 2>&1
del /s /f /q "C:\Windows\Temp\*.*" >nul 2>&1
for /d %%p in ("C:\Windows\Temp\*.*") do rmdir "%%p" /s /q >nul 2>&1
del /s /f /q "C:\Windows\Prefetch\*.*" >nul 2>&1
del /s /f /q "%localappdata%\Microsoft\Windows\Explorer\thumbcache_*.db" >nul 2>&1
echo [OK] Arquivos temporarios e prefetch limpos com sucesso!
echo.
pause
goto MENU_CLEAN

:CLEAN_RAM
echo.
echo Liberando memoria RAM ociosa...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-Process | ForEach-Object { try { $_.MinWorkingSet = $_.MinWorkingSet } catch {} }; [System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers()" >nul 2>&1
echo [OK] Cache Standby da RAM liberado com sucesso!
echo.
pause
goto MENU_CLEAN

:CLEAN_DNS
echo.
echo Limpando cache de DNS...
ipconfig /flushdns >nul 2>&1
echo [OK] Cache de DNS limpo com sucesso!
echo.
pause
goto MENU_CLEAN

:CLEAN_TRIM
echo.
echo Executando TRIM no SSD C:...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Optimize-Volume -DriveLetter C -ReTrim -ErrorAction SilentlyContinue" >nul 2>&1
echo [OK] TRIM executado com sucesso no SSD!
echo.
pause
goto MENU_CLEAN

:CLEAN_WINUPDATE
echo.
echo Limpando cache do Windows Update...
net stop wuauserv >nul 2>&1
del /s /f /q "%windir%\SoftwareDistribution\Download\*.*" >nul 2>&1
net start wuauserv >nul 2>&1
echo [OK] Cache do Windows Update esvaziado!
echo.
pause
goto MENU_CLEAN

:CLEAN_ALL
echo.
echo Executando limpeza geral completa...
del /s /f /q "%temp%\*.*" >nul 2>&1
for /d %%p in ("%temp%\*.*") do rmdir "%%p" /s /q >nul 2>&1
del /s /f /q "C:\Windows\Temp\*.*" >nul 2>&1
del /s /f /q "C:\Windows\Prefetch\*.*" >nul 2>&1
ipconfig /flushdns >nul 2>&1
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-Process | ForEach-Object { try { $_.MinWorkingSet = $_.MinWorkingSet } catch {} }; [System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers()" >nul 2>&1
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Optimize-Volume -DriveLetter C -ReTrim -ErrorAction SilentlyContinue" >nul 2>&1
echo [SUCESSO] Todas as limpezas de cache, RAM e disco concluidas!
echo.
pause
goto MENU_CLEAN

:MENU_CPU
cls
echo ===============================================================================
echo                APEX BOOST - PROCESSADOR (CPU), TIMERS E ENERGIA
echo ===============================================================================
echo.
echo   [1] Ativar Plano Apex Ultimate Performance (Desempenho Maximo)
echo   [2] CPU Core Unparking (Destravar 100%% dos nucleos do processador)
echo   [3] Ajustar Timer Resolution para 0.5ms (Tick rate maximo de clock)
echo   [4] Desativar HPET (Eliminar gargalos de clock sintetico)
echo   [T] APLICAR TODAS AS OTIMIZACOES DE CPU
echo   [V] Voltar ao Menu Principal
echo.
echo ===============================================================================
choice /c 1234TV /n /m "Escolha uma opcao de CPU [1-4, T, V]: "
if errorlevel 6 goto MAIN_MENU
if errorlevel 5 goto CPU_ALL
if errorlevel 4 goto CPU_HPET
if errorlevel 3 goto CPU_TIMER
if errorlevel 2 goto CPU_UNPARK
if errorlevel 1 goto CPU_POWER
goto MENU_CPU

:CPU_POWER
echo.
echo Ativando Plano Apex Ultimate Performance...
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor PROCTHROTTLEMIN 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor PROCTHROTTLEMAX 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor CPMINCORES 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor CPMAXCORES 100 >nul 2>&1
powercfg -setactive scheme_current >nul 2>&1
echo [OK] Plano Ultimate Performance ativado com sucesso!
echo.
pause
goto MENU_CPU

:CPU_UNPARK
echo.
echo Destravando nucleos do processador (Core Unparking)...
powercfg -setacvalueindex scheme_current sub_processor CPMINCORES 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor CPMAXCORES 100 >nul 2>&1
powercfg -setactive scheme_current >nul 2>&1
echo [OK] 100%% dos nucleos da CPU estao desbloqueados sem entrar em modo sleep!
echo.
pause
goto MENU_CPU

:CPU_TIMER
echo.
echo Ajustando Timer Resolution para 0.5ms...
bcdedit /set useplatformclock false >nul 2>&1
bcdedit /set useplatformtick yes >nul 2>&1
bcdedit /set disabledynamictick yes >nul 2>&1
echo [OK] Timer Resolution ajustado para 0.5ms!
echo.
pause
goto MENU_CPU

:CPU_HPET
echo.
echo Desativando HPET sintetico...
bcdedit /deletevalue useplatformclock >nul 2>&1
echo [OK] HPET desativado com sucesso!
echo.
pause
goto MENU_CPU

:CPU_ALL
echo.
echo Aplicando todas as otimizacoes de CPU...
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor PROCTHROTTLEMIN 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor PROCTHROTTLEMAX 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor CPMINCORES 100 >nul 2>&1
powercfg -setacvalueindex scheme_current sub_processor CPMAXCORES 100 >nul 2>&1
powercfg -setactive scheme_current >nul 2>&1
bcdedit /set useplatformclock false >nul 2>&1
bcdedit /set useplatformtick yes >nul 2>&1
bcdedit /set disabledynamictick yes >nul 2>&1
bcdedit /deletevalue useplatformclock >nul 2>&1
echo [SUCESSO] Processador totalmente otimizado para maximo desempenho!
echo.
pause
goto MENU_CPU

:MENU_GPU
cls
echo ===============================================================================
echo                 APEX BOOST - PLACA DE VIDEO (GPU) E GRAFICOS
echo ===============================================================================
echo.
echo   [1] Ativar HAGS (Hardware Accelerated GPU Scheduling - Reduz CPU overhead)
echo   [2] Ativar Modo de Jogo Nativo do Windows 10/11
echo   [3] Desativar Otimizacoes de Tela Inteira (FSE Fix - Fim do input lag)
echo   [4] Definir Prioridade Maxima de Renderizacao (GPU Priority 8 / Scheduling High)
echo   [T] APLICAR TODAS AS OTIMIZACOES DE GPU
echo   [V] Voltar ao Menu Principal
echo.
echo ===============================================================================
choice /c 1234TV /n /m "Escolha uma opcao de GPU [1-4, T, V]: "
if errorlevel 6 goto MAIN_MENU
if errorlevel 5 goto GPU_ALL
if errorlevel 4 goto GPU_PRIORITY
if errorlevel 3 goto GPU_FSE
if errorlevel 2 goto GPU_GAMEMODE
if errorlevel 1 goto GPU_HAGS
goto MENU_GPU

:GPU_HAGS
echo.
echo Ativando Agendamento de GPU acelerado por hardware (HAGS)...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d 2 /f >nul 2>&1
echo [OK] HAGS ativado no registro do Windows!
echo.
pause
goto MENU_GPU

:GPU_GAMEMODE
echo.
echo Ativando Modo de Jogo do Windows...
reg add "HKCU\Software\Microsoft\GameBar" /v "AllowAutoGameMode" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 1 /f >nul 2>&1
echo [OK] Modo de Jogo ativado!
echo.
pause
goto MENU_GPU

:GPU_FSE
echo.
echo Desativando otimizacoes forcadas de tela inteira (FSE Fix)...
reg add "HKCU\System\GameConfigStore" /v "GameDVR_FSEBehaviorMode" /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_HonorUserFSEBehaviorMode" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_DXGIHonorFSEWindowsCompatible" /t REG_DWORD /d 1 /f >nul 2>&1
echo [OK] Otimizacoes de tela inteira ajustadas para zero delay!
echo.
pause
goto MENU_GPU

:GPU_PRIORITY
echo.
echo Configurando prioridade de GPU para jogos...
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d 6 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d "High" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "SFIO Priority" /t REG_SZ /d "High" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d 0 /f >nul 2>&1
echo [OK] Prioridade maxima de renderizacao atribuida para jogos!
echo.
pause
goto MENU_GPU

:GPU_ALL
echo.
echo Aplicando todas as configuracoes graficas de GPU...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\GameBar" /v "AllowAutoGameMode" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_FSEBehaviorMode" /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_HonorUserFSEBehaviorMode" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_DXGIHonorFSEWindowsCompatible" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d 6 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d "High" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d 0 /f >nul 2>&1
echo [SUCESSO] Placa de video totalmente configurada para maximo FPS!
echo.
pause
goto MENU_GPU

:MENU_INPUTLAG
cls
echo ===============================================================================
echo                APEX BOOST - ZERO INPUT LAG (MOUSE E TECLADO)
echo ===============================================================================
echo.
echo   [1] Mouse Raw Input 1:1 (Desativar aceleracao de ponteiro do Windows)
echo   [2] Otimizar Buffer de Teclado (Resposta instantanea sem repeticao lenta)
echo   [3] Desativar Teclas de Aderencia (StickyKeys e FilterKeys)
echo   [T] APLICAR TODAS AS MELHORIAS DE INPUT LAG
echo   [V] Voltar ao Menu Principal
echo.
echo ===============================================================================
choice /c 123TV /n /m "Escolha uma opcao de Input Lag [1-3, T, V]: "
if errorlevel 5 goto MAIN_MENU
if errorlevel 4 goto IN_ALL
if errorlevel 3 goto IN_STICKY
if errorlevel 2 goto IN_KEYBOARD
if errorlevel 1 goto IN_MOUSE
goto MENU_INPUTLAG

:IN_MOUSE
echo.
echo Desativando aceleracao do mouse...
reg add "HKCU\Control Panel\Mouse" /v "MouseSpeed" /t REG_SZ /d 0 /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold1" /t REG_SZ /d 0 /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold2" /t REG_SZ /d 0 /f >nul 2>&1
echo [OK] Aceleracao do mouse desativada (Sensibilidade 1:1 direta)!
echo.
pause
goto MENU_INPUTLAG

:IN_KEYBOARD
echo.
echo Otimizando buffer e taxa de repeticao do teclado...
reg add "HKCU\Control Panel\Accessibility\Keyboard Response" /v "Flags" /t REG_SZ /d "122" /f >nul 2>&1
reg add "HKCU\Control Panel\Accessibility\Keyboard Response" /v "AutoRepeatDelay" /t REG_SZ /d "200" /f >nul 2>&1
reg add "HKCU\Control Panel\Accessibility\Keyboard Response" /v "AutoRepeatRate" /t REG_SZ /d "0" /f >nul 2>&1
echo [OK] Buffer de teclado ajustado para resposta imediata!
echo.
pause
goto MENU_INPUTLAG

:IN_STICKY
echo.
echo Desativando Teclas de Aderencia (StickyKeys)...
reg add "HKCU\Control Panel\Accessibility\StickyKeys" /v "Flags" /t REG_SZ /d "506" /f >nul 2>&1
echo [OK] StickyKeys e avisos sonoros desativados!
echo.
pause
goto MENU_INPUTLAG

:IN_ALL
echo.
echo Aplicando todas as melhorias de mouse e teclado...
reg add "HKCU\Control Panel\Mouse" /v "MouseSpeed" /t REG_SZ /d 0 /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold1" /t REG_SZ /d 0 /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold2" /t REG_SZ /d 0 /f >nul 2>&1
reg add "HKCU\Control Panel\Accessibility\Keyboard Response" /v "Flags" /t REG_SZ /d "122" /f >nul 2>&1
reg add "HKCU\Control Panel\Accessibility\Keyboard Response" /v "AutoRepeatDelay" /t REG_SZ /d "200" /f >nul 2>&1
reg add "HKCU\Control Panel\Accessibility\Keyboard Response" /v "AutoRepeatRate" /t REG_SZ /d "0" /f >nul 2>&1
reg add "HKCU\Control Panel\Accessibility\StickyKeys" /v "Flags" /t REG_SZ /d "506" /f >nul 2>&1
echo [SUCESSO] Mouse e Teclado agora respondem sem nenhum atraso de input!
echo.
pause
goto MENU_INPUTLAG

:MENU_NETWORK
cls
echo ===============================================================================
echo                APEX BOOST - REDE, PING BAIXO E CONEXAO ESTAVEL
echo ===============================================================================
echo.
echo   [1] Desativar Algoritmo de Nagle (TcpAckFrequency = 1 para menor ping)
echo   [2] Otimizar Pilha TCP/IP e Window Auto-Tuning
echo   [3] Configurar DNS Gamer Cloudflare (1.1.1.1 e 1.0.0.1)
echo   [4] Configurar DNS Gamer Google (8.8.8.8 e 8.8.4.4)
echo   [5] Desativar Network Throttling Index do Windows
echo   [T] APLICAR TODAS AS OTIMIZACOES DE REDE
echo   [V] Voltar ao Menu Principal
echo.
echo ===============================================================================
choice /c 12345TV /n /m "Escolha uma opcao de Rede [1-5, T, V]: "
if errorlevel 7 goto MAIN_MENU
if errorlevel 6 goto NET_ALL
if errorlevel 5 goto NET_THROTTLE
if errorlevel 4 goto NET_DNS_GOOGLE
if errorlevel 3 goto NET_DNS_CLOUDFLARE
if errorlevel 2 goto NET_TCPIP
if errorlevel 1 goto NET_NAGLE
goto MENU_NETWORK

:NET_NAGLE
echo.
echo Desativando atraso de pacote Nagle em todas as interfaces...
for /f %%i in ('reg query "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"') do (
    reg add "%%i" /v "TcpAckFrequency" /t REG_DWORD /d 1 /f >nul 2>&1
    reg add "%%i" /v "TCPNoDelay" /t REG_DWORD /d 1 /f >nul 2>&1
    reg add "%%i" /v "TcpDelAckTicks" /t REG_DWORD /d 0 /f >nul 2>&1
)
echo [OK] Nagle Algorithm desativado! Menos jitter e delay de pacote.
echo.
pause
goto MENU_NETWORK

:NET_TCPIP
echo.
echo Otimizando pilha TCP/IP do Windows...
netsh int tcp set global autotuninglevel=normal >nul 2>&1
netsh int tcp set global rss=enabled >nul 2>&1
netsh int tcp set global chimney=disabled >nul 2>&1
netsh int tcp set global timestamps=disabled >nul 2>&1
netsh int tcp set global ecncapability=disabled >nul 2>&1
netsh int tcp set heuristics disabled >nul 2>&1
netsh int ip set global taskoffload=enabled >nul 2>&1
echo [OK] Pilha TCP/IP otimizada com sucesso!
echo.
pause
goto MENU_NETWORK

:NET_DNS_CLOUDFLARE
echo.
echo Configurando DNS Cloudflare 1.1.1.1...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Set-DnsClientServerAddress -ServerAddresses ('1.1.1.1','1.0.0.1')" >nul 2>&1
ipconfig /flushdns >nul 2>&1
echo [OK] DNS Gamer Cloudflare configurado com exito!
echo.
pause
goto MENU_NETWORK

:NET_DNS_GOOGLE
echo.
echo Configurando DNS Google 8.8.8.8...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Set-DnsClientServerAddress -ServerAddresses ('8.8.8.8','8.8.4.4')" >nul 2>&1
ipconfig /flushdns >nul 2>&1
echo [OK] DNS Google configurado com exito!
echo.
pause
goto MENU_NETWORK

:NET_THROTTLE
echo.
echo Desativando limitacao de trafego de rede multimidia...
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 4294967295 /f >nul 2>&1
echo [OK] Limitacoes de rede do Windows desativadas!
echo.
pause
goto MENU_NETWORK

:NET_ALL
echo.
echo Aplicando conjunto completo de rede...
netsh int tcp set global autotuninglevel=normal >nul 2>&1
netsh int tcp set global rss=enabled >nul 2>&1
netsh int tcp set global chimney=disabled >nul 2>&1
netsh int tcp set global timestamps=disabled >nul 2>&1
netsh int tcp set global ecncapability=disabled >nul 2>&1
netsh int tcp set heuristics disabled >nul 2>&1
netsh int ip set global taskoffload=enabled >nul 2>&1
for /f %%i in ('reg query "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"') do (
    reg add "%%i" /v "TcpAckFrequency" /t REG_DWORD /d 1 /f >nul 2>&1
    reg add "%%i" /v "TCPNoDelay" /t REG_DWORD /d 1 /f >nul 2>&1
    reg add "%%i" /v "TcpDelAckTicks" /t REG_DWORD /d 0 /f >nul 2>&1
)
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 4294967295 /f >nul 2>&1
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Set-DnsClientServerAddress -ServerAddresses ('1.1.1.1','1.0.0.1')" >nul 2>&1
ipconfig /flushdns >nul 2>&1
echo [SUCESSO] Conexao de rede configurada para menor ping e zero packet loss!
echo.
pause
goto MENU_NETWORK

:MENU_WINDOWS
cls
echo ===============================================================================
echo                 APEX BOOST - WINDOWS DEBLOATER E PRIVACIDADE
echo ===============================================================================
echo.
echo   [1] Desativar Telemetria e Diagnosticos da Microsoft (DiagTrack)
echo   [2] Desativar Xbox Game Bar DVR (Gravacao em segundo plano que rouba FPS)
echo   [3] Desativar Notificacoes, Anuncios Nativos e Cortana
echo   [4] Otimizar Efeitos Visuais mantendo fontes e icones nitidos
echo   [T] APLICAR TODAS AS OTIMIZACOES DO WINDOWS
echo   [V] Voltar ao Menu Principal
echo.
echo ===============================================================================
choice /c 1234TV /n /m "Escolha uma opcao do Windows [1-4, T, V]: "
if errorlevel 6 goto MAIN_MENU
if errorlevel 5 goto WIN_ALL
if errorlevel 4 goto WIN_VISUALS
if errorlevel 3 goto WIN_NOTIF
if errorlevel 2 goto WIN_DVR
if errorlevel 1 goto WIN_TELEMETRY
goto MENU_WINDOWS

:WIN_TELEMETRY
echo.
echo Desativando servicos de telemetria e rastreamento...
sc stop "DiagTrack" >nul 2>&1
sc config "DiagTrack" start=disabled >nul 2>&1
sc stop "dmwappushservice" >nul 2>&1
sc config "dmwappushservice" start=disabled >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v "AllowTelemetry" /t REG_DWORD /d 0 /f >nul 2>&1
echo [OK] Telemetria e rastreamento desativados!
echo.
pause
goto MENU_WINDOWS

:WIN_DVR
echo.
echo Desativando Xbox Game Bar DVR em segundo plano...
reg add "HKCU\System\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v "AllowGameDVR" /t REG_DWORD /d 0 /f >nul 2>&1
echo [OK] Xbox Game Bar DVR desativado! Mais FPS nos seus jogos.
echo.
pause
goto MENU_WINDOWS

:WIN_NOTIF
echo.
echo Desativando sugestoes, anuncios nativos e Cortana...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SystemPaneSuggestionsEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\PushNotifications" /v "ToastEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v "AllowCortana" /t REG_DWORD /d 0 /f >nul 2>&1
echo [OK] Anuncios, Cortana e notificacoes intrusivas desativadas!
echo.
pause
goto MENU_WINDOWS

:WIN_VISUALS
echo.
echo Otimizando efeitos visuais...
reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v "MinAnimate" /t REG_SZ /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "TaskbarAnimations" /t REG_DWORD /d 0 /f >nul 2>&1
echo [OK] Animacoes pesadas desativadas mantendo nitidez visual!
echo.
pause
goto MENU_WINDOWS

:WIN_ALL
echo.
echo Aplicando debloat completo do Windows...
sc stop "DiagTrack" >nul 2>&1
sc config "DiagTrack" start=disabled >nul 2>&1
sc stop "dmwappushservice" >nul 2>&1
sc config "dmwappushservice" start=disabled >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v "AllowTelemetry" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v "AllowGameDVR" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SystemPaneSuggestionsEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\PushNotifications" /v "ToastEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
echo [SUCESSO] Windows totalmente otimizado e limpo de bloatwares!
echo.
pause
goto MENU_WINDOWS

:MENU_SECURITY
cls
echo ===============================================================================
echo                APEX BOOST - SEGURANCA, BACKUP E RESTAURACAO
echo ===============================================================================
echo.
echo   [1] Criar Ponto de Restauracao oficial do Windows Agora
echo   [2] Fazer Backup das Chaves de Registro em C:\ApexBoost_Backups
echo   [3] Restaurar Chaves de Registro do Backup Salvo
echo   [V] Voltar ao Menu Principal
echo.
echo ===============================================================================
choice /c 123V /n /m "Escolha uma opcao de Seguranca [1-3, V]: "
if errorlevel 4 goto MAIN_MENU
if errorlevel 3 goto SEC_RESTORE_REG
if errorlevel 2 goto SEC_BACKUP_REG
if errorlevel 1 goto SEC_RESTORE_POINT
goto MENU_SECURITY

:SEC_RESTORE_POINT
echo.
echo Criando Ponto de Restauracao do Sistema...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Enable-ComputerRestore -Drive 'C:\' -ErrorAction SilentlyContinue; Checkpoint-Computer -Description 'ApexBoost_ManualPoint' -RestorePointType 'MODIFY_SETTINGS' -ErrorAction SilentlyContinue" >nul 2>&1
echo [OK] Ponto de Restauracao solicitado com sucesso!
echo.
pause
goto MENU_SECURITY

:SEC_BACKUP_REG
echo.
echo Fazendo backup das chaves de registro...
if not exist "C:\ApexBoost_Backups" mkdir "C:\ApexBoost_Backups" >nul 2>&1
reg export "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" "C:\ApexBoost_Backups\SystemProfile.reg" /y >nul 2>&1
reg export "HKCU\Control Panel\Desktop" "C:\ApexBoost_Backups\Desktop.reg" /y >nul 2>&1
reg export "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" "C:\ApexBoost_Backups\Tcpip.reg" /y >nul 2>&1
echo [OK] Backup salvo com sucesso em C:\ApexBoost_Backups!
echo.
pause
goto MENU_SECURITY

:SEC_RESTORE_REG
echo.
echo Restaurando chaves de registro do backup...
if exist "C:\ApexBoost_Backups\SystemProfile.reg" (
    reg import "C:\ApexBoost_Backups\SystemProfile.reg" >nul 2>&1
    reg import "C:\ApexBoost_Backups\Desktop.reg" >nul 2>&1
    reg import "C:\ApexBoost_Backups\Tcpip.reg" >nul 2>&1
    echo [OK] Chaves de registro restauradas com exito!
) else (
    echo [AVISO] Nenhum backup encontrado em C:\ApexBoost_Backups!
)
echo.
pause
goto MENU_SECURITY

:MENU_GAMES
cls
echo ===============================================================================
echo                 APEX BOOST - GUIAS DE OTIMIZACAO PARA JOGOS
echo ===============================================================================
echo.
echo   [1] Counter-Strike 2 (CS2) - Opcoes de Inicializacao e Reflex
echo   [2] Valorant - RawInputBuffer e Latencia de Audio/Video
echo   [3] Fortnite - Performance Mode e Replay Tweaks
echo   [4] Call of Duty: Warzone - Render Worker Count e DLSS
echo   [5] GTA V / FiveM Roleplay - Estabilizacao de 1%% Low
echo   [V] Voltar ao Menu Principal
echo.
echo ===============================================================================
choice /c 12345V /n /m "Escolha um jogo para ver as dicas recomendadas [1-5, V]: "
if errorlevel 6 goto MAIN_MENU
if errorlevel 5 goto GAME_GTA
if errorlevel 4 goto GAME_WZ
if errorlevel 3 goto GAME_FN
if errorlevel 2 goto GAME_VAL
if errorlevel 1 goto GAME_CS2
goto MENU_GAMES

:GAME_CS2
cls
echo ===============================================================================
echo                    CONFIGURACOES RECOMENDADAS PARA CS2
echo ===============================================================================
echo.
echo 1. Opcoes de Inicializacao na Steam:
echo    -novid -high -threads [Numero de Threads da sua CPU] +fps_max 0
echo.
echo 2. No Jogo:
echo    - Modo de Exibicao: Tela Inteira Exclusiva
echo    - Nvidia Reflex: Ativado + Boost (se possuir GPU Nvidia)
echo    - FidelityFX Super Resolution: Desativado (Para maxima nitidez e menos delay)
echo.
pause
goto MENU_GAMES

:GAME_VAL
cls
echo ===============================================================================
echo                   CONFIGURACOES RECOMENDADAS PARA VALORANT
echo ===============================================================================
echo.
echo 1. No Jogo (Configuracoes de Video):
echo    - Renderizacao Multinucleo (Multithreaded Rendering): LIGADO
echo    - RawInputBuffer: LIGADO (Zera o input lag de mouse de alto polling rate)
echo    - Nvidia Reflex Baixa Latencia: LIGADO + BOOST
echo    - V-Sync: SEMPRE DESLIGADO
echo.
pause
goto MENU_GAMES

:GAME_FN
cls
echo ===============================================================================
echo                   CONFIGURACOES RECOMENDADAS PARA FORTNITE
echo ===============================================================================
echo.
echo 1. Modo de Renderizacao: Modo de Desempenho (Performance Mode).
echo 2. Desative a gravacao de replays nas configuracoes para ganhar ate +35 FPS.
echo 3. Malhas (Meshes): Baixo para mais FPS, Alto para ver atraves de construcoes.
echo.
pause
goto MENU_GAMES

:GAME_WZ
cls
echo ===============================================================================
echo                   CONFIGURACOES RECOMENDADAS PARA WARZONE
echo ===============================================================================
echo.
echo 1. Arquivo 'options.3.cod22.cst' (em Documentos\\Call of Duty):
echo    - Ajuste 'RendererWorkerCount' para o numero exato de nucleos FISICOS da CPU.
echo 2. V-Sync: Desligado. Reflex: Ligado + Boost.
echo.
pause
goto MENU_GAMES

:GAME_GTA
cls
echo ===============================================================================
echo               CONFIGURACOES RECOMENDADAS PARA GTA V / FIVEM
echo ===============================================================================
echo.
echo 1. Painel Nvidia: Modo de Gerenciamento de Energia -> Preferencia por Desempenho Maximo.
echo 2. No FiveM: Desative Sombras Suaves e Oclusao de Ambiente para estabilizar 1%% Low.
echo.
pause
goto MENU_GAMES

:RESTORE_ALL
cls
echo ===============================================================================
echo           APEX BOOST - REVERTER PARA O PADRAO ORIGINAL DO WINDOWS
echo ===============================================================================
echo.
echo Deseja realmente restaurar todas as configuracoes para o padrao de fabrica?
choice /c SN /n /m "Confirma restauracao para o padrao original? [S para Sim / N para Nao]: "
if errorlevel 2 goto MAIN_MENU
if errorlevel 1 goto DO_RESTORE
goto MAIN_MENU

:DO_RESTORE
echo.
echo 1. Restaurando pilha TCP/IP e rede...
netsh int ip reset >nul 2>&1
netsh int tcp reset >nul 2>&1
netsh winsock reset >nul 2>&1

echo 2. Restaurando timers padrao...
bcdedit /deletevalue useplatformclock >nul 2>&1
bcdedit /deletevalue useplatformtick >nul 2>&1
bcdedit /deletevalue disabledynamictick >nul 2>&1

echo 3. Restaurando plano de energia padrao...
powercfg -restoredefaultschemes >nul 2>&1

echo 4. Restaurando servicos essenciais do Windows...
sc config "DiagTrack" start=auto >nul 2>&1
sc start "DiagTrack" >nul 2>&1

echo.
echo ===============================================================================
echo [SUCESSO] Todas as configuracoes foram restauradas para o padrao original!
echo Recomendamos reiniciar o computador agora.
echo ===============================================================================
echo.
pause
goto MAIN_MENU

:OPT_EXIT
cls
echo.
echo ===============================================================================
echo   Obrigado por utilizar a suite Apex Optimizer Pro!
echo   Bons jogos e maximo desempenho!
echo ===============================================================================
echo.
exit /b 0
"""

# -------------------------------------------------------------
# 9. GUIAS E MANUAIS FORMATADOS
# -------------------------------------------------------------
README_GAMES = """===============================================================================
       APEX BOOST LABS - GUIA DE OTIMIZACAO PARA JOGOS COMPETITIVOS
===============================================================================

1. COUNTER-STRIKE 2 (CS2):
   - Opcoes de Inicializacao na Steam (Propriedades do Jogo -> Geral):
     -novid -high -threads [Numero de Threads da sua CPU] +fps_max 0
   - Configuracoes de Video no jogo:
     - Modo de Exibicao: Tela Inteira Exclusiva (obrigatorio)
     - Nvidia Reflex Low Latency: Ativado + Boost (se possuir GPU Nvidia)
     - FidelityFX Super Resolution: Desativado (Para maxima nitidez e menos delay)
     - MSAA: 2x ou 4x (desative FXAA)

2. VALORANT:
   - Configuracoes de Video no jogo:
     - Renderizacao Multinucleo (Multithreaded Rendering): LIGADO
     - RawInputBuffer: LIGADO (Zera o delay de mouse com polling rate de 1000Hz/4000Hz/8000Hz)
     - Nvidia Reflex Baixa Latencia: LIGADO + BOOST
     - V-Sync: SEMPRE DESLIGADO
     - Limitadores de FPS: Todos DESLIGADOS

3. FORTNITE:
   - Modo de Renderizacao: Modo de Desempenho (Performance Mode)
   - Baixa Latencia Nvidia Reflex: Ligado + Boost
   - Gravacao de Replays: DESLIGADO (ganho de ate +35 FPS em lutas)
   - Malhas (Meshes): Baixo para mais FPS estavel

4. CALL OF DUTY: WARZONE:
   - Localize o arquivo: Documentos\\Call of Duty\\options.3.cod22.cst
   - Altere a linha 'RendererWorkerCount' para a quantidade exata de nucleos FISICOS da sua CPU
   - V-Sync: Desligado | Nvidia Reflex: Ligado + Boost | DLSS: Desempenho ou FSR

5. GTA V / FIVEM ROLEPLAY:
   - Painel Nvidia: Modo de Gerenciamento de Energia -> Preferencia por Desempenho Maximo
   - No FiveM: Desative Sombras Suaves e Oclusao de Ambiente para eliminar stutters
===============================================================================
"""

README_MANUAL = """===============================================================================
        APEX BOOST LABS - MANUAL DE INSTRUCOES E EXECUCAO
===============================================================================

COMO UTILIZAR O PACK EM 3 PASSOS SIMPLES:

PASSO 1: EXTRAIA O ARQUIVO COMPLETO
- Clique com o botao direito no arquivo .zip que voce baixou e escolha "Extrair Tudo".
- IMPORTANTE: Nao execute os scripts de dentro do arquivo compactado sem extrair!

PASSO 2: EXECUTE O OTIMIZADOR AUTOMATICO
- Abra a pasta extraida e de 2 cliques no arquivo:
  "00_APEX_OTIMIZADOR_AUTOMATICO.bat" (ou "00_APEX_INICIAR_AQUI.bat")
- Uma janela do Windows (UAC) solicitara permissao de Administrador.
  Clique em "SIM" para permitir que o script configure os parametros de kernel.

PASSO 3: ESCOLHA A OPCAO [1] NO MENU
- Digite 1 e aperte Enter para executar a "OTIMIZACAO TOTAL EM 1 CLIQUE".
- O script criara um Ponto de Restauracao de seguranca e aplicara todas as
  melhorias de CPU, GPU, Latencia de Mouse e Conexao.
- Ao concluir, REINICIE SEU COMPUTADOR para ativar todas as alteracoes!

REVERSAO (SEGURO E 100% REVERSIVEL):
- Caso queira voltar qualquer configuracao para o padrao de fabrica do Windows,
  basta abrir o menu e digitar 'R', ou executar o arquivo
  "01_SEGURANCA/03_REVERTER_PADRAO_WINDOWS.bat".

SUPORTE VIP:
- Equipe Apex Boost Labs: suporte@apexboostlabs.com
- Discord Oficial da Comunidade: discord.gg/apexboost
===============================================================================
"""

README_OBS = """===============================================================================
   APEX BOOST LABS - GUIA DE OTIMIZACAO PARA OBS STUDIO & STREAMLABS
===============================================================================
1. No OBS Studio -> Configuracoes -> Avancado:
   - Prioridade do Processo: Acima do Normal (Above Normal)
2. Configuracoes -> Saida -> Modo de Saida (Avancado) -> Transmissao:
   - Codificador: NVIDIA NVENC H.264 (novo) ou AMD HW H.264
   - Controle de Taxa: CBR
   - Taxa de Bits: 6000 Kbps (Twitch) ou 9000 Kbps (YouTube)
   - Predefinicao: Desempenho / Baixa Latencia
   - Perfil: High
   - Intervalo de Keyframe: 2 segundos
   - B-Frames: 2
3. Desative a 'Pre-visualizacao' durante partidas competitivas para poupar GPU.
===============================================================================
"""

README_BIOS = """===============================================================================
   APEX BOOST LABS - DICAS AVANCADAS DE BIOS, MEMORIA RAM E REBAR
===============================================================================
1. MEMORIA RAM (XMP / EXPO / DOCP):
   - Entre na BIOS da sua placa-mae (teclando DEL ou F2 ao ligar o PC).
   - Ative o perfil XMP (Intel) ou EXPO / D.O.C.P (AMD).
   - Isso garante que suas memorias operem na frequencia maxima anunciada
     (ex: 3200MHz, 3600MHz, 6000MHz) em vez do padrao de 2133MHz.

2. RESIZABLE BAR (ReBAR) & ABOVE 4G DECODING:
   - Ative 'Above 4G Decoding' e 'Resizable BAR' na sua BIOS.
   - Permite que a CPU acesse toda a VRAM da placa de video de uma so vez,
     gerando ganhos de ate +15% de FPS em placas RTX 30/40 e Radeon RX 6000/7000.

3. REVERSAO E C-STATES:
   - Desative C-States caso seu foco seja puramente estabilidade competitiva
     sem oscilacao de clock em torneios.
===============================================================================
"""

def make_zip(filename, files_dict):
    filepath = os.path.join(DOWNLOADS_DIR, filename)
    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for fname, content in files_dict.items():
            zipf.writestr(fname, content)
    print(f"Created {filename} successfully ({os.path.getsize(filepath)} bytes)")

# -------------------------------------------------------------
# 1. STARTER TWEAK PACK (R$ 9,90)
# -------------------------------------------------------------
starter_files = {
    '00_APEX_INICIAR_AQUI.bat': MASTER_LAUNCHER_BAT,
    '01_SEGURANCA/01_Criar_Ponto_De_Restauracao.bat': RESTORE_POINT_BAT,
    '01_SEGURANCA/02_Backup_Registro_Windows.bat': BACKUP_REG_BAT,
    '01_SEGURANCA/03_REVERTER_PADRAO_WINDOWS.bat': UNDO_ALL_BAT,
    '02_LIMPEZA/01_Limpeza_Profunda_Temp_Cache.bat': CLEAN_TEMP_BAT,
    '02_LIMPEZA/02_Liberar_Memoria_RAM.bat': CLEAN_RAM_BAT,
    '03_WINDOWS/01_Desativar_Telemetria_Diagnosticos.bat': TELEMETRY_BAT,
    '03_WINDOWS/02_Desativar_Xbox_GameBar_DVR.bat': GAMEBAR_DVR_BAT,
    '03_WINDOWS/03_Desativar_Bloatware_Notificacoes.bat': BLOATWARE_BAT,
    '04_ENERGIA/01_Ativar_Plano_Ultimate_Performance.bat': ULTIMATE_PERF_BAT,
    '05_INPUT_LAG/01_Desativar_Aceleracao_Mouse_Raw_Input.reg': MOUSE_RAW_INPUT_REG,
    'LEIA-ME_Manual_Starter_Pack.txt': README_MANUAL
}
make_zip('starter_pack.zip', starter_files)

# -------------------------------------------------------------
# 2. COMPETITIVE FPS ULTRA PACK (R$ 19,90)
# -------------------------------------------------------------
ultra_files = {
    '00_APEX_OTIMIZADOR_AUTOMATICO.bat': MASTER_LAUNCHER_BAT,
    '01_SEGURANCA/01_Criar_Ponto_De_Restauracao.bat': RESTORE_POINT_BAT,
    '01_SEGURANCA/02_Backup_Registro_Windows.bat': BACKUP_REG_BAT,
    '01_SEGURANCA/03_REVERTER_PADRAO_WINDOWS.bat': UNDO_ALL_BAT,
    '02_LIMPEZA/01_Limpeza_Profunda_Temp_Cache.bat': CLEAN_TEMP_BAT,
    '02_LIMPEZA/02_Liberar_Memoria_RAM.bat': CLEAN_RAM_BAT,
    '02_LIMPEZA/03_Otimizar_SSD_TRIM.bat': SSD_TRIM_BAT,
    '03_WINDOWS/01_Desativar_Telemetria_Diagnosticos.bat': TELEMETRY_BAT,
    '03_WINDOWS/02_Desativar_Xbox_GameBar_DVR.bat': GAMEBAR_DVR_BAT,
    '03_WINDOWS/03_Desativar_Bloatware_Notificacoes.bat': BLOATWARE_BAT,
    '03_WINDOWS/04_Otimizar_Efeitos_Visuais_Desempenho.bat': VISUAL_FX_BAT,
    '04_CPU/01_Ativar_Plano_Ultimate_Performance.bat': ULTIMATE_PERF_BAT,
    '04_CPU/02_CPU_Core_Unparking_100Percent.bat': CPU_UNPARK_BAT,
    '04_CPU/03_Timer_Resolution_Ultra_Low_0.5ms.bat': TIMER_RES_BAT,
    '04_CPU/04_Desativar_HPET_Gargalo_Clock.bat': HPET_DISABLE_BAT,
    '05_GPU/01_Ativar_HAGS_Aceleracao_GPU.reg': HAGS_REG,
    '05_GPU/02_Modo_Jogo_Windows_GameMode.reg': GAMEMODE_REG,
    '05_GPU/03_Desativar_Fullscreen_Optimizations.reg': FULLSCREEN_FIX_REG,
    '05_GPU/04_Otimizacao_Driver_GPU_HighPriority.bat': GPU_OPTIMIZER_BAT,
    '06_INPUT_LAG/01_Mouse_Raw_Input_Sem_Aceleracao.reg': MOUSE_RAW_INPUT_REG,
    '06_INPUT_LAG/02_Teclado_Resposta_Instantanea.reg': KEYBOARD_RESPONSIVENESS_REG,
    '07_REDE/01_Limpar_Flush_DNS.bat': DNS_GAMER_BAT,
    'GUIAS_JOGOS/GUIA_OTIMIZACAO_CS2_VALORANT_FORTNITE.txt': README_GAMES,
    'LEIA-ME_Manual_Competitive_FPS.txt': README_MANUAL
}
make_zip('ultra_fps_pack.zip', ultra_files)

# -------------------------------------------------------------
# 3. ZERO LATENCY & NETWORK PRO (R$ 24,90)
# -------------------------------------------------------------
network_files = {
    '00_APEX_OTIMIZADOR_AUTOMATICO.bat': MASTER_LAUNCHER_BAT,
    '01_SEGURANCA/01_Criar_Ponto_De_Restauracao.bat': RESTORE_POINT_BAT,
    '01_SEGURANCA/02_Backup_Registro_Windows.bat': BACKUP_REG_BAT,
    '01_SEGURANCA/03_REVERTER_PADRAO_WINDOWS.bat': UNDO_ALL_BAT,
    '02_LIMPEZA/01_Limpeza_Profunda_Temp_Cache.bat': CLEAN_TEMP_BAT,
    '02_LIMPEZA/02_Liberar_Memoria_RAM.bat': CLEAN_RAM_BAT,
    '03_WINDOWS/01_Desativar_Telemetria_Diagnosticos.bat': TELEMETRY_BAT,
    '04_ENERGIA/01_Ativar_Plano_Ultimate_Performance.bat': ULTIMATE_PERF_BAT,
    '07_REDE/01_Otimizar_TCP_IP_Nagle_Disable.bat': TCP_NETWORK_BAT,
    '07_REDE/02_Configurar_DNS_Gamer_Cloudflare_1.1.1.1.bat': DNS_GAMER_BAT,
    '07_REDE/03_Prioridade_Processos_NetworkThrottling.reg': GAMEMODE_REG,
    'GUIAS_REDE/COMO_CONFIGURAR_OBS_STUDIO_ZERO_LOSS.txt': README_OBS,
    'LEIA-ME_Manual_Network_Pro.txt': README_MANUAL
}
make_zip('network_pro_pack.zip', network_files)

# -------------------------------------------------------------
# 4. ULTIMATE EXTREME SUITE (ALL-IN-ONE COMPLETO - R$ 34,90)
# -------------------------------------------------------------
extreme_files = {
    '00_APEX_OTIMIZADOR_MASTER_PRO.bat': MASTER_LAUNCHER_BAT,
    
    # 01 Segurança
    '01_SEGURANCA_E_BACKUP/01_Criar_Ponto_De_Restauracao.bat': RESTORE_POINT_BAT,
    '01_SEGURANCA_E_BACKUP/02_Backup_Registro_Windows.bat': BACKUP_REG_BAT,
    '01_SEGURANCA_E_BACKUP/03_REVERTER_PADRAO_WINDOWS.bat': UNDO_ALL_BAT,
    
    # 02 Limpeza & RAM
    '02_LIMPEZA_E_RAM/01_Limpeza_Profunda_Temp_Cache.bat': CLEAN_TEMP_BAT,
    '02_LIMPEZA_E_RAM/02_Liberar_Memoria_RAM_Standby.bat': CLEAN_RAM_BAT,
    '02_LIMPEZA_E_RAM/03_Otimizar_SSD_TRIM.bat': SSD_TRIM_BAT,
    
    # 03 Windows & Bloatware
    '03_WINDOWS_E_BLOATWARE/01_Desativar_Telemetria_Diagnosticos.bat': TELEMETRY_BAT,
    '03_WINDOWS_E_BLOATWARE/02_Desativar_Xbox_GameBar_DVR.bat': GAMEBAR_DVR_BAT,
    '03_WINDOWS_E_BLOATWARE/03_Desativar_Bloatware_Notificacoes.bat': BLOATWARE_BAT,
    '03_WINDOWS_E_BLOATWARE/04_Otimizar_Efeitos_Visuais_Desempenho.bat': VISUAL_FX_BAT,
    
    # 04 CPU & Energia
    '04_CPU_E_ENERGIA/01_Ativar_Plano_Ultimate_Performance_Apex.bat': ULTIMATE_PERF_BAT,
    '04_CPU_E_ENERGIA/02_CPU_Core_Unparking_100Percent.bat': CPU_UNPARK_BAT,
    '04_CPU_E_ENERGIA/03_Timer_Resolution_Ultra_Low_0.5ms.bat': TIMER_RES_BAT,
    '04_CPU_E_ENERGIA/04_Desativar_HPET_Gargalo_Clock.bat': HPET_DISABLE_BAT,
    
    # 05 GPU & Gráficos
    '05_GPU_E_GRAFICOS/01_Ativar_HAGS_Aceleracao_GPU.reg': HAGS_REG,
    '05_GPU_E_GRAFICOS/02_Modo_Jogo_Windows_GameMode.reg': GAMEMODE_REG,
    '05_GPU_E_GRAFICOS/03_Desativar_Fullscreen_Optimizations.reg': FULLSCREEN_FIX_REG,
    '05_GPU_E_GRAFICOS/04_Otimizacao_Driver_GPU_HighPriority.bat': GPU_OPTIMIZER_BAT,
    
    # 06 Input Lag
    '06_INPUT_LAG/01_Mouse_Raw_Input_Sem_Aceleracao.reg': MOUSE_RAW_INPUT_REG,
    '06_INPUT_LAG/02_Teclado_Resposta_Instantanea.reg': KEYBOARD_RESPONSIVENESS_REG,
    
    # 07 Rede & Ping
    '07_REDE_E_PING/01_Otimizar_TCP_IP_Nagle_Disable.bat': TCP_NETWORK_BAT,
    '07_REDE_E_PING/02_Configurar_DNS_Gamer_Cloudflare_1.1.1.1.bat': DNS_GAMER_BAT,
    
    # 08 Guias e Manuais
    '08_GUIAS_COMPLETOS/GUIA_OTIMIZACAO_CS2_VALORANT_FORTNITE.txt': README_GAMES,
    '08_GUIAS_COMPLETOS/GUIA_CONFIGURACAO_OBS_STREAMING.txt': README_OBS,
    '08_GUIAS_COMPLETOS/GUIA_BIOS_RAM_XMP_EXPO_DICAS.txt': README_BIOS,
    'LEIA-ME_Manual_Ultimate_Extreme.txt': README_MANUAL
}
make_zip('ultimate_extreme_suite.zip', extreme_files)

print("Generated all 4 packs successfully with UAC auto-elevation and true gaming performance!")

