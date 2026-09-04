#!/usr/bin/env python3
import json
import threading
from datetime import datetime
from dataclasses import asdict
from pathlib import Path
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import core

class Window(Gtk.Window):
    def __init__(self):
        super().__init__(title='Zebra RAW • GC420t')
        self.set_default_size(900, 760)
        self.set_border_width(18)
        self.connect('destroy', Gtk.main_quit)
        self.busy = False
        self.path = None
        self.widgets = {}
        self.jobs = []
        try:
            self.state = core.load_profiles()
        except (ValueError, OSError):
            self.state = {'profiles': {'Padrão': asdict(core.Settings())}, 'selected': 'Padrão'}
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(root)
        title = Gtk.Label(xalign=0)
        title.set_markup('<span size="xx-large" weight="bold">Zebra RAW</span>   GC420t · USB · 203 dpi')
        root.pack_start(title, False, False, 0)
        row = Gtk.Box(spacing=8)
        root.pack_start(row, False, False, 0)
        row.pack_start(Gtk.Label(label='Impressora USB'), False, False, 0)
        self.printer = Gtk.ComboBoxText()
        row.pack_start(self.printer, True, True, 0)
        self.button(row, 'Atualizar', self.refresh)
        self.status = Gtk.Label(label='Pronto', xalign=0)
        root.pack_end(self.status, False, False, 0)
        notebook = Gtk.Notebook()
        root.pack_start(notebook, True, True, 0)
        printing = self.page(notebook, 'Imprimir')
        self.note(printing, 'Envie .zpl ou .txt diretamente à impressora, sem filtros de texto.')
        self.file_label = Gtk.Label(label='Nenhum arquivo selecionado', xalign=0)
        self.file_label.set_ellipsize(3)
        printing.pack_start(self.file_label, False, False, 0)
        row = Gtk.Box(spacing=8); printing.pack_start(row, False, False, 0)
        self.button(row, 'Escolher arquivo…', self.choose)
        self.button(row, 'Recarregar', self.reload)
        self.preview = self.textview(printing)
        row = Gtk.Box(spacing=8); printing.pack_start(row, False, False, 0)
        row.pack_start(Gtk.Label(label='Repetições do arquivo'), False, False, 0)
        self.repeats = Gtk.SpinButton.new_with_range(1, 100, 1)
        row.pack_start(self.repeats, False, False, 0)
        self.note(printing, 'Cada repetição mantém todas as etiquetas e quantidades (^PQ) do arquivo.')
        self.apply_first = Gtk.CheckButton(label='Enviar as configurações desta interface antes do arquivo')
        printing.pack_start(self.apply_first, False, False, 0)
        self.note(printing, 'O arquivo é preservado byte a byte. Comandos nele podem substituir os ajustes enviados antes.\nA visualização abaixo é do código, não uma simulação da etiqueta.')
        self.button(printing, 'Enviar arquivo RAW', self.print_file)
        config = self.page(notebook, 'Configuração e perfis')
        row = Gtk.Box(spacing=8); config.pack_start(row, False, False, 0)
        self.profile = Gtk.ComboBoxText.new_with_entry()
        for name in self.state['profiles']: self.profile.append_text(name)
        self.profile.get_child().set_text(self.state.get('selected', 'Padrão'))
        row.pack_start(self.profile, True, True, 0)
        self.button(row, 'Carregar perfil', self.load_profile)
        self.button(row, 'Salvar perfil local', self.save_profile)
        grid = Gtk.Grid(column_spacing=24, row_spacing=10)
        config.pack_start(grid, False, False, 0)
        fields = [('width','Largura de impressão (mm)',1,104,.125), ('length','Comprimento da etiqueta (mm)',1,990,.125),
                  ('speed','Velocidade (pol/s — 2 a 4)',2,4,1), ('darkness','Intensidade (0 a 30)',0,30,1),
                  ('top','Ajuste vertical (dots)',-120,120,1), ('left','Deslocamento à esquerda (dots)',-9999,9999,1),
                  ('tear','Posição de destaque (dots)',-120,120,1)]
        for i,(key,label,low,high,step) in enumerate(fields):
            grid.attach(Gtk.Label(label=label, xalign=0),0,i,1,1)
            w=Gtk.SpinButton.new_with_range(low,high,step); w.set_digits(3 if step<1 else 0)
            self.widgets[key]=w; grid.attach(w,1,i,1,1)
        for i,(key,label,options) in enumerate([
            ('method','Método',[('T','Transferência térmica (ribbon)'),('D','Térmico direto (sem ribbon)')]),
            ('media','Detecção da mídia',[('Y','Espaço / entalhe'),('M','Marca preta'),('N','Contínua'),('A','Automática')])],len(fields)):
            grid.attach(Gtk.Label(label=label,xalign=0),0,i,1,1)
            w=Gtk.ComboBoxText()
            for code,text in options: w.append(code,text)
            self.widgets[key]=w; grid.attach(w,1,i,1,1)
        self.note(config,'8 dots = 1 mm · Largura máxima impressa: 104 mm. A largura não redimensiona o conteúdo.\nComprimento sem o espaço entre etiquetas; em mídia com espaço o sensor determina o passo.\nModo de saída: destaque manual. Os valores são do perfil local, não uma leitura da impressora.')
        self.persist=Gtk.CheckButton(label='Gravar também na memória da impressora (^JUS) ao aplicar')
        config.pack_start(self.persist,False,False,0)
        row=Gtk.Box(spacing=8);config.pack_start(row,False,False,0)
        self.button(row,'Ver comandos ZPL',self.show_commands)
        self.button(row,'Aplicar na impressora',self.apply_config)
        self.button(row,'Exportar configuração…',self.export)
        maintenance=self.page(notebook,'Manutenção e fila')
        self.note(maintenance,'As ações abaixo enviam comandos reais. Calibrar pode avançar várias etiquetas.\nO estado do CUPS não informa diretamente falta de ribbon, papel ou tampa aberta; confira o LED.')
        row=Gtk.Box(spacing=8);maintenance.pack_start(row,False,False,0)
        self.button(row,'Calibrar mídia',lambda *_:self.command('Calibrar mídia',b'~JC', 'A calibração avançará etiquetas. Continuar?'))
        self.button(row,'Imprimir configuração',lambda *_:self.command('Configuração da impressora',b'~WC'))
        self.button(row,'Etiqueta de teste',self.test_label)
        self.button(maintenance,'Atualizar estado e fila CUPS',self.queue)
        self.queue_text=self.textview(maintenance)
        self.button(maintenance,'Cancelar último trabalho deste aplicativo',self.cancel_last)
        self.note(maintenance,'Cancelar no CUPS não recolhe dados que já chegaram à impressora.')
        history=self.page(notebook,'Registro')
        self.logview=self.textview(history)
        self.note(history,'Registro da sessão. “Aceito pelo CUPS” não confirma impressão física.')
        self.load_profile()
        self.refresh()

    def page(self, notebook, title):
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10);box.set_border_width(16)
        notebook.append_page(box,Gtk.Label(label=title));return box
    def note(self,box,text):
        label=Gtk.Label(label=text,xalign=0);label.set_line_wrap(True);box.pack_start(label,False,False,0)
    def button(self,box,text,fn):
        b=Gtk.Button(label=text);b.connect('clicked',fn);box.pack_start(b,False,False,0);return b
    def textview(self,box):
        view=Gtk.TextView();view.set_editable(False);view.set_monospace(True);view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        scroll=Gtk.ScrolledWindow();scroll.set_min_content_height(110);scroll.add(view);box.pack_start(scroll,True,True,0);return view
    def set_text(self,view,text):view.get_buffer().set_text(text)
    def log(self,text):
        buf=self.logview.get_buffer();buf.insert(buf.get_end_iter(),datetime.now().strftime('%H:%M:%S')+'  '+text+'\n')
    def error(self,e):
        self.log(str(e));self.dialog(str(e),Gtk.MessageType.ERROR)
    def dialog(self,text,kind=Gtk.MessageType.INFO,confirm=False):
        d=Gtk.MessageDialog(transient_for=self,modal=True,message_type=kind,buttons=Gtk.ButtonsType.OK_CANCEL if confirm else Gtk.ButtonsType.OK,text=text)
        result=d.run();d.destroy();return result==Gtk.ResponseType.OK
    def task(self,fn,done):
        if self.busy:return self.dialog('Aguarde a operação atual.')
        self.busy=True;self.status.set_text('Processando…')
        def worker():
            try: result=fn();GLib.idle_add(finish,result,None)
            except Exception as e:GLib.idle_add(finish,None,e)
        def finish(result,error):
            self.busy=False;self.status.set_text('Pronto' if not error else 'Falha — veja o registro')
            if error:self.error(error)
            else:done(result)
            return False
        threading.Thread(target=worker,daemon=True).start()
    def refresh(self,*_):
        def done(rows):
            old=self.printer.get_active_id();self.printer.remove_all()
            for name,uri in rows:self.printer.append(name,name+' — GC420t USB')
            self.printer.set_active_id(old or 'Zebra')
            if self.printer.get_active()<0:self.printer.set_active(0)
            self.status.set_text('GC420t USB encontrada' if rows else 'Nenhuma fila GC420t USB encontrada no CUPS')
        self.task(core.printers,done)
    def settings(self):
        values={k:(w.get_active_id() if isinstance(w,Gtk.ComboBoxText) else w.get_value() if k in ('width','length') else w.get_value_as_int()) for k,w in self.widgets.items()}
        s=core.Settings(**values);s.validate();return s
    def load_profile(self,*_):
        try:
            name=self.profile.get_child().get_text();s=core.Settings(**self.state['profiles'][name]);s.validate()
            for key,w in self.widgets.items():
                if isinstance(w,Gtk.ComboBoxText):w.set_active_id(getattr(s,key))
                else:w.set_value(getattr(s,key))
        except Exception as e:self.error(e)
    def save_profile(self,*_):
        try:
            name=self.profile.get_child().get_text().strip()
            if not name:raise ValueError('Dê um nome ao perfil.')
            new=name not in self.state['profiles'];self.state['profiles'][name]=asdict(self.settings());self.state['selected']=name
            core.save_profiles(self.state)
            if new:self.profile.append_text(name)
            self.log('Perfil salvo localmente: '+name)
        except Exception as e:self.error(e)
    def choose(self,*_):
        d=Gtk.FileChooserDialog(title='Escolher ZPL',transient_for=self,action=Gtk.FileChooserAction.OPEN)
        d.add_buttons('Cancelar',Gtk.ResponseType.CANCEL,'Abrir',Gtk.ResponseType.OK)
        f=Gtk.FileFilter();f.set_name('ZPL e texto');[f.add_pattern(p) for p in ['*.zpl','*.txt','*.ZPL','*.TXT']];d.add_filter(f)
        if d.run()==Gtk.ResponseType.OK:self.path=d.get_filename()
        d.destroy();self.reload()
    def reload(self,*_):
        if not self.path:return
        try:
            data=core.read_zpl(self.path);self.file_label.set_text(f'{self.path} • {len(data):,} bytes • {data.count(b"^XA")} formato(s)')
            self.set_text(self.preview,data[:100000].decode('utf-8',errors='replace')+ ('\n[Visualização truncada; envio integral]' if len(data)>100000 else ''))
        except Exception as e:self.error(e)
    def send(self,data,title,repeats=1):
        printer=self.printer.get_active_id()
        def done(result):
            import re
            match=re.search(r'request id is (\S+)',result)
            if match:self.jobs.append(match[1])
            self.log(title+': '+result);self.status.set_text('Aceito pelo CUPS — confira a impressora')
        self.task(lambda:core.submit(printer,data,title,repeats),done)
    def print_file(self,*_):
        try:
            if not self.path:raise ValueError('Escolha um arquivo primeiro.')
            data=core.read_zpl(self.path)
            if self.apply_first.get_active():data=self.settings().zpl()+data
            self.send(data,Path(self.path).name,self.repeats.get_value_as_int())
        except Exception as e:self.error(e)
    def command(self,title,data,question=None):
        if question and not self.dialog(question,confirm=True):return
        self.send(data,title)
    def apply_config(self,*_):
        try:
            data=self.settings().zpl(self.persist.get_active())
            if self.persist.get_active() and not self.dialog('Gravar os ajustes na impressora? ^JUS salva todos os parâmetros persistentes atuais.',confirm=True):return
            self.send(data,'Aplicar configuração')
        except Exception as e:self.error(e)
    def show_commands(self,*_):
        try:self.dialog(self.settings().zpl(self.persist.get_active()).decode())
        except Exception as e:self.error(e)
    def export(self,*_):
        try:data=self.settings().zpl(self.persist.get_active())
        except Exception as e:return self.error(e)
        d=Gtk.FileChooserDialog(title='Exportar ZPL',transient_for=self,action=Gtk.FileChooserAction.SAVE)
        d.add_buttons('Cancelar',Gtk.ResponseType.CANCEL,'Salvar',Gtk.ResponseType.OK);d.set_current_name('configuracao.zpl');d.set_do_overwrite_confirmation(True)
        if d.run()==Gtk.ResponseType.OK:
            try:Path(d.get_filename()).write_bytes(data)
            except Exception as e:self.error(e)
        d.destroy()
    def test_label(self,*_):
        try:
            s=self.settings()
            if s.width<40 or s.length<25:raise ValueError('Para esta etiqueta de teste, use ao menos 40 × 25 mm.')
            data=s.zpl()+f'^XA^FO8,8^GB{round(s.width*8)-16},{round(s.length*8)-16},2^FS^FO20,25^A0N,25,20^FDZebra GC420t^FS^FO20,65^A0N,20,16^FDRAW USB - 203 dpi^FS^FO20,100^BY2^BCN,50,N,N,N^FD123456^FS^PQ1^XZ'.encode()
            self.send(data,'Etiqueta de teste')
        except Exception as e:self.error(e)
    def queue(self,*_):
        printer=self.printer.get_active_id()
        if not printer:return self.dialog('Selecione uma impressora.')
        self.task(lambda:core.run(['lpstat','-p',printer,'-l'])+'\n\n'+core.run(['lpstat','-o',printer]),lambda text:self.set_text(self.queue_text,text))
    def cancel_last(self,*_):
        if not self.jobs:return self.dialog('Nenhum trabalho enviado nesta sessão.')
        job=self.jobs[-1]
        if self.dialog('Cancelar o trabalho '+job+' no CUPS?',confirm=True):
            self.task(lambda:core.run(['cancel',job]),lambda _: (self.jobs.remove(job),self.log('Cancelado no CUPS: '+job)))

if __name__=='__main__':
    win=Window();win.show_all();Gtk.main()
