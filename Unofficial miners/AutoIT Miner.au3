; ###########################################
; #        Duino-Coin miner version 0.4     #
; # https://github.com/revoxhere/duino-coin #
; #       copyright by MrKris7100 2019      #
; ###########################################

#Region ;**** Directives created by AutoIt3Wrapper_GUI ****
#AutoIt3Wrapper_Change2CUI=y
#EndRegion ;**** Directives created by AutoIt3Wrapper_GUI ****
#include <Crypt.au3>
Global $shares[2], $socket, $last_hash_count = 0, $hash_Count = 0, $pool_address, $pool_port, $username, $password
If Not FileExists(@ScriptDir & "\config.ini") Then
	ConsoleWrite("Initial configuration, you can edit 'config.ini' later" & @CRLF & @CRLF)
	ConsoleWrite("Enter pool adddress (official: serveo.net): ")
	$pool_address = Cin()
	IniWrite(@ScriptDir & "\config.ini", "pool", "address", $pool_address)
	ConsoleWrite("Enter pool port (official: 14808): ")
	$pool_port = Cin()
	IniWrite(@ScriptDir & "\config.ini", "pool", "port", $pool_port)
	ConsoleWrite("Enter username: ")
	$username = Cin()
	IniWrite(@ScriptDir & "\config.ini", "pool", "username", $username)
	ConsoleWrite("Enter password: ")
	$password = Cin()
	IniWrite(@ScriptDir & "\config.ini", "pool", "password", $password)
Else
	$pool_address = IniRead(@ScriptDir & "\config.ini", "pool", "address", "0")
	$pool_port = IniRead(@ScriptDir & "\config.ini", "pool", "port", "0")
	$username = IniRead(@ScriptDir & "\config.ini", "pool", "username", "0")
	$password = IniRead(@ScriptDir & "\config.ini", "pool", "password", "0")
EndIf
TCPStartup()
While 1
	ConsoleWrite("Connecting to pool..." & @CRLF)
	$socket = TCPConnect(TCPNameToIP($pool_address), $pool_port)
	If @error Then
		ConsoleWrite(@error & " Cannot connect to pool server. Retrying in 30 seconds..." & @CRLF)
		Sleep(30000)
	Else
		ConsoleWrite("Connected!" & @CRLF)
		ExitLoop
	EndIf
	Sleep(25)
WEnd
ConsoleWrite("Logging in..." & @CRLF)
TCPSend($socket, "LOGI," & $username & "," & $password)
While 1
	$resp = TCPRecv($socket, 1024)
	If $resp = "OK" Then
		ConsoleWrite("Logged in!" & @CRLF)
		ExitLoop
	EndIf
	If $resp = "NO" Then
		ConsoleWrite("Error, closing in 5 seconds...")
		TCPCloseSocket($socket)
		Sleep(5000)
		Exit
	EndIf
	Sleep(25)
WEnd
ConsoleWrite("Start mining..." & @CRLF)
AdlibRegister("hush", 1000)
While 1
	TCPSend($socket, "JOB")
	While 1
		$job = TCPRecv($socket, 1024)
		If $job Then ExitLoop
		Sleep(25)
	WEnd
	$job = StringSplit($job, ",", 2)
	ConsoleWrite("Recived new job from pool. Diff: " & $job[2] & @CRLF)
	For $iJob = 0 To 100 * $job[2]
		$hash = StringLower(StringTrimLeft(_Crypt_HashData($job[0] & $iJob, 0x00008004), 2))
		$hash_count += 1
		If $job[1] = $hash Then
			TCPSend($socket, StringToBinary($iJob, 4))
			While 1
				$good = TCPRecv($socket, 1024)
				If $good = "GOOD" Then
					$shares[0] += 1 ; Share accepted
					ConsoleWrite("Share accepted " & $shares[0] & "/" & $shares[0] + $shares[1] & " (" & StringLeft($shares[0] / ($shares[0] + $shares[1]) * 100, 4) & "%), " & $last_hash_count & " H/s" & @CRLF)
					ExitLoop
				ElseIf $good = "BAD" Then
					$shares[1] += 1 ; SHare rejected
					ConsoleWrite("Share rejected " & $shares[0] & "/" & $shares[0] + $shares[1] & " (" & StringLeft($shares[0] / ($shares[0] + $shares[1]) * 100, 4) & "%), " & $last_hash_count & " H/s" & @CRLF)
					ExitLoop
				EndIf
				Sleep(25)
			WEnd
			ExitLoop
		EndIf
	Next
WEnd
Func hush()
	$last_hash_count = $hash_count
	$hash_count = 0
EndFunc
func Cin()
    Local $sResult
    Local $sText
    While True
        $sText = ConsoleRead()
        If @error Then ExitLoop
        if StringRight($sText, 1) = @LF then
            Return StringTrimRight($sText, 1)
        EndIf
        Sleep(20)
    WEnd
EndFunc
