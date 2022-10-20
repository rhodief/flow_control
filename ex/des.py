import curses
from curses import wrapper, noecho, use_default_colors, newpad
from curses.textpad import rectangle
import threading
import time
from typing import Dict


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
        self._boxed_types = ['Sequence', 'Map', 'Parallel']
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
                self.echo(f'Time : <{duration}>')
                c = '█░'
                self.echo(''.join([c for i in range(80)]))

            self.backward_ident()
        else:
            info = duration
            if status == 'R':
                info = 'RUNNING'
            self.echo(f'{index}: {name} - ({info})', color_status, True, False, True)
            if status == 'R' and parent_type == 'Sequence':
                self.forward_ident()
                self.echo(f'Time : <{duration}>')
                self.echo(f'Ulogger: <{logs}>')
                self.backward_ident()

def main():
    design = {
        'header': {
            'title': 'Meu Fluxo Teste',
            'type': 'Flow Control',
            'configs': ''
        },
        'flows': [
            {
                'type': 'Sequence',
                'name': 'Carregamento DataSet',
                'index': '0',
                'status':'R',
                'executors': [
                    {
                        'type': 'Function',
                        'name': 'CarregarListaDeIds',
                        'duration': '25s',
                        'status': 'OK',
                        'index': '0.0'
                    },
                    {
                        'type': 'Function',
                        'name': 'Verificando Existência dos Arquivos',
                        'duration': '25s',
                        'status': 'R',
                        'index': '0.1',
                        'logs': 'Pergunta teste: será um um texto maluco maior que todos oqs dkd skskskd dkdkdkjf fkfkfjd fkj'
                    }
                ]
            }
        ]
    }
    design2 = {
        'header': {
            'title': 'Meu Fluxo Map',
            'type': 'Flow Control',
            'configs': ''
        },
        'flows': [
            {
                'type': 'Sequence',
                'name': 'Carregamento DataSet',
                'index': '0',
                'status':'OK',
                'executors': [
                    {
                        'type': 'Function',
                        'name': 'CarregarListaDeIds',
                        'duration': '25s',
                        'status': 'OK',
                        'index': '0.0'
                    },
                    {
                        'type': 'Function',
                        'name': 'Verificando Existência dos Arquivos',
                        'duration': '25s',
                        'status': 'OK',
                        'index': '0.1',
                        'logs': 'Pergunta teste: será um um texto maluco maior que todos oqs dkd skskskd dkdkdkjf fkfkfjd fkj'
                    }
                ]
            },
            {
                'type': 'Map',
                'name': 'Processamento dos Registros',
                'index': '1',
                'status':'R',
                'duration': 28,
                'executors': [
                    {
                        'type': 'Function',
                        'name': 'Abrir Arquivos',
                        'status': 'R',
                        'index': '1.0'
                    },
                    {
                        'type': 'Function',
                        'name': 'ConverterParaDicionario',
                        'status': 'R',
                        'index': '1.1',
                        'logs': 'Looog 1'
                    },
                    {
                        'type': 'Function',
                        'name': 'Predição Modelo',
                        'status': 'R',
                        'index': '1.2',
                        'logs': 'Loog 2 2  Mais um textos'
                    }
                ]
            }
        ]
    }
    design3 = {
        'header': {
            'title': 'Meu Fluxo Parallel',
            'type': 'Flow Control',
            'configs': ''
        },
        'flows': [
            {
                'type': 'Sequence',
                'name': 'Carregamento DataSet',
                'index': '0',
                'status':'OK',
                'executors': [
                    {
                        'type': 'Function',
                        'name': 'CarregarListaDeIds',
                        'duration': '25s',
                        'status': 'OK',
                        'index': '0.0'
                    },
                    {
                        'type': 'Function',
                        'name': 'Verificando Existência dos Arquivos',
                        'duration': '25s',
                        'status': 'OK',
                        'index': '0.1',
                        'logs': 'Pergunta teste: será um um texto maluco maior que todos oqs dkd skskskd dkdkdkjf fkfkfjd fkj'
                    }
                ]
            },
            {
                'type': 'Map',
                'name': 'Processamento dos Registros',
                'index': '1',
                'status':'OK',
                'executors': [
                    {
                        'type': 'Function',
                        'name': 'Abrir Arquivos',
                        'status': 'OK',
                        'index': '1.0',
                        'duration': '25s',
                    },
                    {
                        'type': 'Function',
                        'name': 'ConverterParaDicionario',
                        'status': 'OK',
                        'index': '1.1',
                        'logs': 'Looog 1',
                        'duration': '25s',
                    },
                    {
                        'type': 'Function',
                        'name': 'Predição Modelo',
                        'status': 'OK',
                        'index': '1.2',
                        'logs': 'Loog 2 2  Mais um textos',
                        'duration': '25s',
                    }
                ]
            },
            {
                'type': 'Parallel',
                'name': 'Aplicação das Análises nos Resultados do Modelo',
                'index': '2',
                'status':'R',
                'executors': [
                    {
                        'type': 'Sequence',
                        'name': 'Carregamento DataSet',
                        'index': '2.1',
                        'status':'OK',
                        'executors': [
                            {
                                'type': 'Function',
                                'name': 'CarregarListaDeIds',
                                'duration': '25s',
                                'status': 'OK',
                                'index': '2.1.0'
                            },
                            {
                                'type': 'Function',
                                'name': 'Verificando Existência dos Arquivos',
                                'duration': '25s',
                                'status': 'OK',
                                'index': '2.1.1',
                                'logs': 'Pergunta teste: será um um texto maluco maior que todos oqs dkd skskskd dkdkdkjf fkfkfjd fkj'
                            }
                        ]
                    },
                    {
                        'type': 'Map',
                        'name': 'Processamento dos Registros',
                        'index': '2.1',
                        'status':'OK',
                        'executors': [
                            {
                                'type': 'Function',
                                'name': 'Abrir Arquivos',
                                'status': 'OK',
                                'index': '2.1.0',
                                'duration': '25s',
                            },
                            {
                                'type': 'Function',
                                'name': 'ConverterParaDicionario',
                                'status': 'OK',
                                'index': '2.1.1',
                                'logs': 'Looog 1',
                                'duration': '25s',
                            },
                            {
                                'type': 'Function',
                                'name': 'Predição Modelo',
                                'status': 'OK',
                                'index': '2.1.2',
                                'logs': 'Loog 2 2  Mais um textos',
                                'duration': '25s',
                            }
                        ]
                    }
                ]
            }
        ]
    }
    t = TerminalDraw()
    def worker(t: TerminalDraw):
        for d in [design, design2, design3]:
            time.sleep(5)
            t.draw(d)
    th = threading.Thread(target=worker, args=(t,), daemon=True)
    th.start()
    wrapper(t)
    
    



if __name__ == '__main__':
    main()