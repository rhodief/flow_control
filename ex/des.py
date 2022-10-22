import curses
from curses import wrapper, noecho, use_default_colors, newpad
from curses.textpad import rectangle
import threading
import time
from typing import Dict
import datetime


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
    design4 = {'header': {'name': 'My Flow', 'type': 'Flow', 'index': '0'}, 'flows': [{'type': 'Sequence', 'name': 'Sequence', 'index': '0.0', 'status': 'OK', 'executors': [{'type': 'function', 'name': 'somar_cinco', 'index': '0.0.0', 'status': 'OK', 'start': datetime.datetime(2022, 10, 22, 15, 16, 16, 915523), 'end': datetime.datetime(2022, 10, 22, 15, 16, 16, 915562)}, {'type': 'Multiplica', 'name': 'Multiplica', 'index': '0.0.1', 'status': 'OK', 'start': datetime.datetime(2022, 10, 22, 15, 16, 16, 915582), 'end': datetime.datetime(2022, 10, 22, 15, 16, 20, 918829)}]}, {'type': 'Map', 'name': 'Map', 'index': '0.1', 'status': 'OK', 'executors': [{'type': 'Multiplica', 'name': 'Multiplica', 'index': '0.1.0', 'status': 'OK', 'total_bar': 6, 'iter_bar': [0, 5, 2, 1, 3, 4]}, {'type': 'Multiplica', 'name': 'Multiplica', 'index': '0.1.1', 'status': 'OK', 'total_bar': 6, 'iter_bar': [0, 1, 5, 3, 4, 2]}, {'type': 'Multiplica', 'name': 'Multiplica', 'index': '0.1.2', 'status': 'OK', 'total_bar': 6, 'iter_bar': [0, 1, 4, 2, 5, 3]}], 'start': datetime.datetime(2022, 10, 22, 15, 16, 28, 929051), 'end': datetime.datetime(2022, 10, 22, 15, 16, 32, 932518), 'status_bar': (18, 18)}, {'type': 'Parallel', 'name': 'Parallel', 'index': '0.2', 'status': 'S', 'start': None, 'end': None, 'executors': [{'type': 'Flow', 'name': 'My Flow', 'index': '0.2.0', 'status': 'OK', 'start': None, 'end': None, 'executors': [{'type': 'Sequence', 'name': 'Sequence', 'index': '0.2.0.0', 'status': 'OK', 'executors': [{'type': 'function', 'name': 'somar_cinco', 'index': '0.2.0.0.0', 'status': 'OK', 'start': datetime.datetime(2022, 10, 22, 15, 16, 32, 933387), 'end': datetime.datetime(2022, 10, 22, 15, 16, 32, 933419)}, {'type': 'Multiplica', 'name': 'Multiplica', 'index': '0.2.0.0.1', 'status': 'OK', 'start': datetime.datetime(2022, 10, 22, 15, 16, 32, 933438), 'end': datetime.datetime(2022, 10, 22, 15, 16, 36, 934844)}]}]}, {'type': 'Flow', 'name': 'My Flow', 'index': '0.2.1', 'status': 'OK', 'start': None, 'end': None, 'executors': [{'type': 'Map', 'name': 'Map', 'index': '0.2.1.0', 'status': 'OK', 'executors': [{'type': 'Multiplica', 'name': 'Multiplica', 'index': '0.2.1.0.0', 'status': 'OK', 'total_bar': 6, 'iter_bar': [0, 2, 1, 3, 5, 4]}, {'type': 'Multiplica', 'name': 'Multiplica', 'index': '0.2.1.0.1', 'status': 'OK', 'total_bar': 6, 'iter_bar': [2, 0, 1, 3, 4, 5]}, {'type': 'Multiplica', 'name': 'Multiplica', 'index': '0.2.1.0.2', 'status': 'OK', 'total_bar': 6, 'iter_bar': [0, 2, 1, 4, 3, 5]}], 'start': datetime.datetime(2022, 10, 22, 15, 16, 40, 943542), 'end': datetime.datetime(2022, 10, 22, 15, 16, 44, 947028), 'status_bar': (18, 18)}]}]}, {'type': 'Sequence', 'name': 'Sequence', 'index': '0.3', 'status': 'OK', 'executors': [{'type': 'function', 'name': '<lambda>', 'index': '0.3.0', 'status': 'OK', 'start': datetime.datetime(2022, 10, 22, 15, 16, 44, 948026), 'end': datetime.datetime(2022, 10, 22, 15, 16, 44, 948055)}]}]}
    t = TerminalDraw()
    def worker(t: TerminalDraw):
        for d in [design, design2, design3, design4]:
            time.sleep(5)
            t.draw(d)
    th = threading.Thread(target=worker, args=(t,), daemon=True)
    th.start()
    wrapper(t)
    
    



if __name__ == '__main__':
    main()