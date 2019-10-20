@echo off
:: SSH Server. Used in Official Duino-Coin network. 
:: Forwards TCP connections (because we can't forward ports, and it's more secure).

::14808 is the default, it won't work hovewer because we are already using it.
set port=14808
::60 is the default, used to prevent connection timing out.
set keepAliveInterval=60

:ssh
ssh -o ServerAliveInterval=%keepAliveInterval% -R %port%:localhost:%port% serveo.net
ping localhost -n 1 >nul
goto ssh
