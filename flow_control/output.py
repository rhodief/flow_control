
from platform import node
from typing import Any, Dict, List, Tuple
import threading
from queue import Queue
import curses
from curses import wrapper, noecho, use_default_colors, newpad
from curses.textpad import rectangle

class Broker:
    def __init__(self, q:Queue) -> None:
        self._queue = q
    def put(self, msg):
        self._queue.put(msg)
    def get(self):
        return self._queue.get()
    def done(self):
        return self._queue.task_done()
    def block(self):
        return self._queue.join()

class FlowDesign:
    def __init__(self) -> None:
        self._main_dict = {}
        self._design = {}
    def __call__(self, event: Dict) -> Any:
        self._build_main_dict(event)
        d = self._build_design()
        return d
    def _build_main_dict(self, event: Dict):
        if event.get('name'):
            name = event.get('name')
            ntype = event.get('type')
            nindex = event.get('index')
            self._main_dict['header'] = {
                "name": name,
                "type": ntype,
                "index": nindex
            }
            self._main_dict['flows'] = self._build_flows(event.get('children'))
        elif event.get('type'):
            ntype = event.get('type')
            parent = event.get('parent')
            current = event.get('current')
            node = self._get_by_index(self._main_dict['flows'], current['index'])
            parent_node = self._get_by_index(self._main_dict['flows'], parent['index'])
            if parent['type'] == 'Sequence':
                if ntype == 'start':
                    node['status'] = 'R'
                    node['start'] = current['start']
                if ntype == 'finish':
                    node['status'] = 'OK'
                    node['end'] = current['end']
                    len_parent = len(parent_node['executors'])
                    last_index = int(node['index'].split('.')[-1])
                    if len_parent == last_index + 1:
                        parent_node['status'] = 'OK'                        
            elif parent['type'] == 'Map':
                if ntype == 'start':
                    if 'status' in parent_node and parent_node['status'] != 'R':
                        parent_node['status'] = 'R'
                        parent_node['start'] = current['start']
                    node['status'] = 'R'
                if ntype == 'finish':
                    parent_node['end'] = current['end']
                    node['total_bar'] = current.get('total_iter')
                    if 'iter_bar' not in node:
                        node['iter_bar'] = []    
                    node['iter_bar'].append(current.get('n_iter'))
                    if len(node['iter_bar']) == node['total_bar']:
                        node['status'] = 'OK'
                        is_all_ok = [exec_nodes['status'] == 'OK' for exec_nodes in parent_node['executors']]
                        if is_all_ok:
                            parent_node['status'] = 'OK'
                        
    def _build_design(self):
        main = {**self._main_dict}
        flows = self._build_design_flows(main['flows'])
        main['flows'] = flows
        return main
    def _build_design_flows(self, list_flow: List[Dict]):
        nodes = []
        for l in list_flow:
            ntype = l.get('type')
            n = l
            '''
            if ntype == 'Sequence':
                #status = l.get('status') if not self._check_chl_all_ok(n['executors']) else 'OK'
                n =  {
                    "type": ntype,
                    "name": l['name'],
                    "index": l['index'],
                    "status": status,
                    "start": l.get('start', None),
                    "end": l.get('end', None),
                    "executors": self._check_executors_status(l['executors'], status)
                }
                if ntype == 'Map':
                status = l.get('status', None) if not l.get('end') else 'OK'
                n =  {
                    "type": ntype,
                    "name": l['name'],
                    "index": l['index'],
                    "status": status,
                    "start": l.get('start', None),
                    "end": l.get('end', None),
                    "total_bar": self._build_total_bar(l['executors']),
                    "executors": self._check_executors_status(l['executors'], status)
                }
            '''
            if ntype == 'Map':
                n = {**l}
                n['status_bar'] = self._build_status_bar(l['executors'])
            
            
            elif ntype in ('Parallel', 'Flow'):
                status = l.get('status') if not self._check_chl_all_ok(l['executors']) else 'OK'
                n =  {
                    "type": ntype,
                    "name": l['name'],
                    "index": l['index'],
                    "status": status,
                    "start": l.get('start', None),
                    "end": l.get('end', None),
                    "executors": self._build_design_flows(l['executors'])
                }
            nodes.append(n)
        return nodes
    def _build_status_bar(self, executors: List[Dict]):
        total_iter = 0
        n_iter = 0
        for e in executors:
            if e.get('total_bar'):
                total_iter = e.get('total_bar') * len(executors)
            n_iter+= len(e.get('iter_bar', []))
        ## normalize values
        return n_iter, total_iter
    def _check_executors_status(self, executors: List[Dict], status: str):
        if status == 'OK':
            for e in executors:
                e['status'] = 'OK'
        return executors
    def _check_chl_all_ok(self, executors: List[Dict]):
        return all([e.get('status') == 'OK' for e in executors])
    def _build_flows(self, node_list: List[Dict]):
        r = []
        for node in node_list:
            chld = []
            if 'children' in node:
                chld = self._build_flows(node['children'])
            e = {
                "type": node['type'],
                "name": node['name'],
                "index": node['index'],
                "status": "S"
            }
            if len(chld) > 0:
                e['executors'] = chld
            r.append(e)
        return r
    def _get_by_index(self, my_list, index:str):
        for item in my_list:
            if item['index'] == index:
                return item
            if 'executors' in item:
                i = self._get_by_index(item['executors'], index)
                if i: return i

       
class TerminalDraw:
    def __init__(self, design = {}) -> None:
        self._designs = design
        self._design = None
        self._stdscr = None
        self.height = None
        self.width = None
        self.mypad_height = 32767
        self.my_pad = None
        self.mypad_pos = [0]
        self._line_pos = [3]
        self._ident = [2]
        self.line_space = 2
        self.ident_space = 2
        self._boxed_types = ['Sequence', 'Map', 'Parallel', 'Flow']
        self._status_color = {
            'R': 1,
            'OK': 3,
            'E': 4
        }
        self.is_loop_running = False
        self._refresh_counters = {}
    @property
    def pad_pos(self):
        return self.mypad_pos[0]
    @pad_pos.setter
    def pad_pos(self, value):
        self.mypad_pos[0] = value
    @property
    def line_pos(self):
        return self._line_pos[0]
    @line_pos.setter
    def line_pos(self, value):
        self._line_pos[0] = value
    @property
    def ident(self):
        return self._ident[0]
    @ident.setter
    def ident(self, value):
        self._ident[0] = value
    
    def forward_ident(self):
        self.ident+= self.ident_space 
    def backward_ident(self):
        self.ident-=self.ident_space
    
    def refresh(self):
        self.mypad.refresh(self.pad_pos+2, 0, 0, 0, self.height-1, self.width)
    def set_color_pair(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, -1) # -1 is for background default color
        curses.init_pair(2, curses.COLOR_CYAN, -1) # -1 is for background default color
        curses.init_pair(3, curses.COLOR_GREEN, -1) # -1 is for background default color
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
    def config(self):
        self._stdscr.keypad(True)
        use_default_colors()
        self.pad_pos = 0
        self.line_pos = 3
        self.ident = 2
        self.is_loop_running = False
        noecho()
        self._stdscr.refresh()
        # Get screen width/height
        self.height, self.width = self._stdscr.getmaxyx()
        self.mypad = newpad(self.mypad_height, self.width)
        #Init colors
        self.mypad.scrollok(True)
        self.set_color_pair()
        self._stdscr.nodelay(1)
        curses.curs_set(0)
    def __call__(self, stdscr) -> None:
        # set everything..
        # draw header
        self._stdscr = stdscr
        self.config()
        self._design = {}
        self._main_draw()
    def _main_draw(self):
        self.config()
        self.draw_header()
        self.draw_body()
        self.draw_footer()
        self.refresh()
        self.is_loop_running = True
        while self.is_loop_running:
            ch = self._stdscr.getch()
            if ch < 0:
                continue
            if ch == curses.KEY_DOWN and self.pad_pos < self.mypad.getyx()[0] - self.height - 1:
                self.pad_pos += 1
                self.refresh()
            elif ch == curses.KEY_UP and self.pad_pos > -2:
                self.pad_pos -= 1
                self.refresh()
            elif ch < 256 and chr(ch) == 'q':
                running = False
            elif ch == curses.KEY_RESIZE:
                self.height,self.width = self._stdscr.getmaxyx()
                while self.pad_pos > self.mypad.getyx()[0] - self.height - 1:
                    self.pad_pos -= 1
                self.refresh()
        self._main_draw()
    def draw(self, design: Dict):
        self._design = design
        self.is_loop_running = False
        
    def echo(self, text: str, n_color_pair: int = 1, bold: bool = False, draw_rectangle = False, underline = False, pos_config = {}):
        self.mypad.attron(curses.color_pair(n_color_pair))
        if draw_rectangle: 
            self.line_pos+=1
            rectangle(self.mypad, self.line_pos - 1, self.ident -1 , self.line_pos + 1, 80)
        if bold: self.mypad.attron(curses.A_BOLD)
        if underline: self.mypad.attron(curses.A_UNDERLINE)
        # Rendering title
        self.mypad.addstr(self.line_pos, self.ident,text)
        if self.line_pos > self.height: self.pad_pos = min(self.line_pos - self.height, self.mypad_height - self.height)
        # Turning off attributes for title
        self.mypad.attroff(curses.color_pair(n_color_pair))
        if underline: self.mypad.attroff(curses.A_UNDERLINE)
        if bold: self.mypad.attroff(curses.A_BOLD)
        self.line_pos+=self.line_space
    def draw_header(self):
        design = self._design
        title = design.get('header', {}).get('title', 'Flow Control')
        ftype = design.get('header', {}).get('type', 'Waitting...')
        text_title = f'>> {title} - {ftype}'
        #### Draw the Header
        self.echo(text_title, 2, True, True)
    def draw_body(self):
        design = self._design
        flows = design.get('flows', [])
        self.forward_ident()
        for flow in flows:
            self.draw_flow_node(flow, 'Flow')
    def draw_footer(self):
        pass
    def draw_flow_node(self, node: Dict, parent_type: str):
        mtype = node.get('type')
        name = node.get('name')
        status = node['status']
        #if status == 'S': return
        color_status = self._status_color.get(status, 2)
        index = node.get('index')
        duration = node.get('duration')
        executors = node.get('executors', [])
        logs = node.get('logs')
        if mtype in self._boxed_types:
            #Desenha com baixa e procura filhos
            self.echo(f'{index}: {name} - {mtype}', color_status, True, True)
            self.forward_ident()
            for executor in executors:
                self.draw_flow_node(executor, mtype)
            if mtype == 'Map' and status == 'R':
                ok_num, total_num = node.get('status_bar', (None, None))
                #print(ok_num, total_num)
                ok_item = '█'
                remain_item = '░'
                #self.echo(f'Time : <{duration}>')
                if total_num <=0: return
                factor = ok_num/total_num
                total_bar = 50
                ok_bar = [ok_item for _ in range(int(factor * total_bar))]
                remain_bar = [remain_item for _ in range(total_bar - len(ok_bar))]
                percent = factor * 100
                bar = ''.join([*ok_bar, *remain_bar])
                self.echo(f'{bar} {ok_num}/{total_num} ({percent:.2f})%')

            self.backward_ident()
        else:
            info = duration
            if status == 'R':
                info = 'RUNNING'
            self.echo(f'{index}: {name} - ({info})', color_status, True, False, True)
            if status == 'R' and parent_type == 'Sequence':
                self.forward_ident()
                #self.echo(f'Time : <{duration}>')
                #self.echo(f'Ulogger: <{logs}>')
                self.backward_ident()

    
             

    
class PrinterWorker():
    def __init__(self) -> None:
        self._draw = FlowDesign()
    def __call__(self, broker, terminal: TerminalDraw) -> Any:
        while True:
            event  = broker.get()
            design = self._draw(event)
            #print(design)
            terminal.draw(design)
            broker.done()
    def subscribe(self):
        '''
        PrinterWorker will execute a function post defined
        '''
        
            
class SuperPrinter():
    '''
    This is responsable to expose the application logs.
    '''
    def __init__(self, broker: Broker, exposingWorker: PrinterWorker) -> None:
        self._broker = broker
        self._bd = {}
        self._terminal_draw = TerminalDraw()
        def w_terminal(terminal_draw: TerminalDraw):
            wrapper(terminal_draw)
        self._thread = threading.Thread(target=exposingWorker, args=(self._broker, self._terminal_draw), daemon=True)
        self._thread_terminal = threading.Thread(target=w_terminal, args=(self._terminal_draw,), daemon=False)        
    def watch(self):
        self._thread_terminal.start()
        self._thread.start()
    def block(self):
        self._broker.block()



