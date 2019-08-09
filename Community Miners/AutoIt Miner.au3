; Special thanks to MrKris7100 for making AutoIt PC miner!
; Feel free to test the code and post the results

#NoTrayIcon
TCPStartup()
Global $connection, $hash_count
 
$hWin = GUICreate("duino-coin GUI miner v1.0", 250, 80)
GUICtrlCreateLabel("Server address", 5, 5)
$hAddress = GUICtrlCreateInput("serveo.net", 80, 5, 75, 20)
GUICtrlCreateLabel("Port", 160, 5)
$hPort = GUICtrlCreateInput("14808", 180, 5, 50, 20)
GUICtrlCreateLabel("Username", 5, 30)
$hUsername = GUICtrlCreateInput("", 65, 30, 75, 20)
GUICtrlCreateLabel("Password", 5, 55)
$hPassword = GUICtrlCreateInput("", 65, 55, 75, 20)
$hHashrate = GUICtrlCreateLabel("Speed: 0 H/s", 150, 30)
$hMine = GUICtrlCreateButton("Start mining", 150, 55)
GUISetState()
While 1
    Switch GUIGetMsg()
        Case -3
            Exit
        Case $hMine
            If LoginToPool(GUICtrlRead($hAddress), _
            GUICtrlRead($hPort), _
            GUICtrlRead($hUsername), _
            GUICtrlRead($hPassword)) Then
                StartMining()
                TCPCloseSocket($connection)
            EndIf
    EndSwitch
    Sleep(25)
WEnd
 
Func hashrate()
    GUICtrlSetData($hHashrate, "Speed: " & $hash_count & " H/s")
    $hash_count = 0
EndFunc
 
Func LoginToPool($server, $port, $username, $password)
    $connection = TCPConnect(TCPNameToIP($server), $port)
    TCPSend($connection, "LOGI")
    Sleep(100)
    TCPSend($connection, $username)
    Sleep(100)
    TCPSend($connection, $password)
    Sleep(100)
    $logged = False
    $timeout = TimerInit()
    While Not ($logged And TimerGet($timeout) < 10000)
        $logged = TCPRecv($connection, 2)
        Sleep(25)
    WEnd
    Return $logged = "OK" ? True : False
EndFunc
 
Func TimerGet($handle)
    Return TimerDiff($handle)
EndFunc
 
Func StartMining()
    TCPSend($connection, "MINE")
    Sleep(1000)
    $hash_count = 0
    AdlibRegister("hashrate", 1000)
    GUICtrlSetData($hMine, "Stop mining")
    While 1
        Switch GUIGetMsg()
            Case -3
                Exit
            Case $hMine
                ExitLoop
        EndSwitch
        $work = Random(0, 9, 1)
        $work2 = Random(0, 9, 1)
        TCPSend($connection, StringToBinary($work + $work2 * $work2 + $work * $work, 4))
        $hash_count += 1
        Sleep(150)
    WEnd
    GUICtrlSetData($hMine, "Start mining")
    AdlibUnRegister("hashrate")
    GUICtrlSetData($hHashrate, "Speed: 0 H/s")
EndFunc
