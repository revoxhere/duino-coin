-- Special thanks to Alina for translating arduino code to NodeMCU!
-- Feel free to test the code and post the results

work = ""
work2 = ""
waiting = 0

uart.on("data", 0, function(data) --check for connection establishment key
    if data == "1" then
        waiting = 1
        print("CONNECTED") --feedback for the miner
    elseif waiting == 1 then
        waiting = 2
        work = data
    elseif waiting == 2 then
        waiting = 0
        work2 = data
        local hash = work+work2*work2+work*work --hash the work
        print(hash) --send back the result
    end
end, 0)
