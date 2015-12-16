#! /usr/bin/python3

from pipe import Pipe

import threading 
import json
import sys



"""
read line in a pipe and parse it to call a function with given args
ex -> ["print", "un", "deux, "trois","soleil"] will be the same than
print("un","deux", "trois", "soleil")
"""
def parsePipe(event, fctArray):
    pipe = Pipe("/tmp/bibusPipe")
    for line in pipe.readlines():
        if not event.isSet():
            return
        try:
            args = json.loads(line)
        except ValueError:
            continue

        if not isinstance(args, list):
            continue

        try:
            command = args.pop(0)
        except IndexError:
            continue

        try:
            fct = fctArray[command]
        except IndexError:
            continue

        fct(*args)

def main():
    interface = "logs"
    if len(sys.argv)>1:
        interface = sys.argv[1]
    if interface == "leds":
        from bibus2Leds import Bibus2Leds
        iBibus = Bibus2Leds
    elif interface == "logs":
        from bibus2Logs import Bibus2Logs
        iBibus = Bibus2Logs
    else:
        raise ValueError("Values in data/interface  should be 'leds' or 'logs'")


    event = threading.Event()
    event.set()
    b = iBibus()

    def quit(*args):
        event.clear()
        b.kill()
        print("quit is taken in count, could be quite long before exit")
    
    fctArray = {
            "print": print,
            "quit" : quit,
            "reloadDefaultJSON": lambda *args: b.load(),
            "loadFile": lambda *args: b.load(args[0]),
            "setUpdateInterval": lambda *args: b.setUpdateInterval(args[0]),
            "killPipeReading": lambda *args: event.clear()
            }

    try:
        thread = threading.Thread(target = parsePipe, args = (event,fctArray))

        thread.start()
        b.start()

    except KeyboardInterrupt:
        quit()


if __name__=="__main__":
    main()


