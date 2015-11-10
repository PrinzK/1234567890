import curses
import time
# giving the current window to curses
stdscr = curses.initscr()
# disable displaying the input
curses.noecho()
# no need to press enter
curses.cbreak()
# return special keys
#stdscr.keypad(1)



try:
    stdscr.addstr(0, 0, "Current mode: Typing mode", curses.A_STANDOUT)
    stdscr.refresh()
    time.sleep(1)
    try:
        while True:
            # non-blocking input
            stdscr.nodelay(1)
            c = stdscr.getch()
            if ord('6') == c:
                c = stdscr.getch()
                if ord('p') == c :            
                    stdscr.addstr(0, 0, "hurray", curses.A_BLINK)
                    stdscr.refresh()
    except curses.ERR:
        pass
                
finally:
    curses.nocbreak(); stdscr.keypad(0); curses.echo()
    curses.endwin()


