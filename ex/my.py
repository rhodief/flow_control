from curses import wrapper, noecho, use_default_colors, newpad, KEY_DOWN, KEY_UP, KEY_RESIZE
from curses.textpad import rectangle
import time
mypad_contents = []

def header(stdscr):
    stdscr.keypad(True)
    use_default_colors()
    noecho()
    stdscr.refresh()

    # Get screen width/height
    height,width = stdscr.getmaxyx()

    # Create a curses pad (pad size is height + 10)
    mypad_height = 32767
    
    mypad = newpad(mypad_height, width)
    mypad.scrollok(True)
    mypad_pos = [0]
    #rectangle(mypad, 1, 0, 5, 30)
    mypad_refresh = lambda: mypad.refresh(mypad_pos[0]+2, 0, 0, 0, height-1, width)
    mypad_refresh()

    def imprimir(val):
        mypad.addstr("{0} This is a sample string...\n".format(i))
        if i > height: mypad_pos[0] = min(i - height, mypad_height - height)
        mypad_refresh()
        #time.sleep(0.05)

    try:
        for i in range(0, 100):
            imprimir(i)
        # Wait for user to scroll or quit
        running = True
        while running:
            ch = stdscr.getch()
            if ch == KEY_DOWN and mypad_pos[0] < mypad.getyx()[0] - height - 1:
                mypad_pos[0] += 1
                mypad_refresh()
            elif ch == KEY_UP and mypad_pos[0] > -2:
                mypad_pos[0] -= 1
                mypad_refresh()
            elif ch < 256 and chr(ch) == 'q':
                running = False
            elif ch == KEY_RESIZE:
                height,width = stdscr.getmaxyx()
                while mypad_pos > mypad.getyx()[0] - height - 1:
                    mypad_pos -= 1
                    mypad_refresh()
            #mypad.addstr('kkkkkkk \n')
            #mypad_refresh()
        
    except KeyboardInterrupt: pass
    '''
    # Store the current contents of pad
    for i in range(0, mypad.getyx()[0]):
        mypad_contents.append(mypad.instr(i, 0))
    '''
    


def main():
    wrapper(header)


if __name__ == '__main__':
    main()