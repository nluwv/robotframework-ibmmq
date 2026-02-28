# MQLibrary voor Robot Framework

## Installatie

Er zijn nogal wat afhankelijkheden met andere componenten die je eerst moet installeren.

# 🧱 Stap 1 — Installeer C++ Build Tools
1. Open de downloadpagina: Ga naar [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) en download de Visual C++ Build Tools Installer.
2. Start de installatie: Start het installatieprogramma. Selecteer Visual Studio Build Tools 2026 en klik op Installeren.
3. Wijzig de installatie (na installatie): Wanneer de Visual Studio Installer opent, klik op Modify bij Build Tools 2026.
4. In het tabblad Workloads onder de categorie Desktop & Mobile, vink aan: 
   ✅ Desktop development with C++
4. Vink nu rechts onder Installation Details de volgende optionele onderdelen aan : (Alle andere optional components mogen uitgevinkt worden)
   ✅ MSVC Build Tools for x64/86 (latest)
   ✅ C++ CMake tools for Windows
   ✅ Windows 11 SDK (v10.0.26...)
6. Start installatie: Klik rechtsonder op Modify om de installatie te starten.



<!-- 
🧰 Alternatief: zonder Build Tools (optioneel)
Gebruik dit alleen als Visual Studio Build Tools niet beschikbaar is.
C++ compiler (LLVM): Download via https://github.com/llvm/llvm-project ➤ Gebruik LLVM-20.1.3-win64.exe → Kies Add to PATH tijdens de installatie
CMake (Wheel builder): Download via https://cmake.org/download/ ➤ Gebruik cmake-4.0.1-windows-x86_64.msi → Kies Add to PATH tijdens de installatie 
-->


# 📥 Stap 2 — Installeer de IBMMQLibrary
1. Open een nieuw terminalvenster
2. Voer de installatie uit:
`pip install robotframework-ibmmq`


# 🔐 Extra — MQ Administrator kanaal activeren (alleen indien nodig)
1. Ga in IBM MQ Explorer naar je Queue Manager
2. Rechtermuisklik → Remote Administration
3. Zorg dat de channel én listener bestaan én actief zijn
4. Gebruik SYSTEM.ADMIN.SVRCONN als channel bij het verbinden




*** Settings ***
Library   IBMMQLibrary

*** Test cases ***
Test connect MQ
    Connect MQ
    ...    queue_manager=<QM_ABCD>
    ...    hostname=uwva2vltunm0123.t-dc.ba.uwv.nl
    ...    port=1414
    ...    channel=<CHANNEL_NAME>
    ...    username=${NONE}
    ...    password=${NONE}
    Disconnect All MQ Connections

