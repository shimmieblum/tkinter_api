from enum import Enum
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import *
import uuid
from uuid import UUID
import tkinter.ttk as ttk

# this tracks whether a tkinter form has already been created. 
# If it has, a new form will actually be a child of this one, or of a specified parent
parent_screen = None 

class Content_type(Enum):
    BUTTON = 'button'
    ENTRY = 'entry'
    TEXT = 'text'
    LABEL = 'label'
    OPTIONS = 'options'
    CHECKBOX = 'checkbox'


class TextWrapper:
    def __init__(self, text:Text) -> None:
        self.text = text
    
    def get(self):
        return self.text.get('1.0',END)



class Form:
    def __init__(self, width, height, title, parent=None):
        ''' creates the form with width and height specified
        @param parent: the parent screen if a form will create a child form
        to run the form, call mainloop() '''

        if parent_screen == None and parent != None: self.create_new_screen(width, height, title)
        elif parent == None: self.additional_window(width, height, title, parent)
        else: self.additional_window(width, height, title, parent_screen)
        self.contents = {}
        self.info = []
        self.widget_maker = Widget_Maker(self.screen)

    ''' === methods for to add widgets === '''

    def additional_window(self, width, height, title, parent):
        self.screen = Toplevel(parent)
        self.screen.geometry(f'{width}x{height}')
        self.screen.title(title)
        
    def generate_child(self, width, height, title):
        ''' create a child of this form and return the Form object '''
        form = Form(width, height, title, parent=self.screen)
        return form

    def create_new_screen(self, width, height, title):
        ''' create a new screen and destroy the old one '''
        if self.screen != None: self.screen.destroy() 
        self.screen = tk.Tk()
        self.screen.geometry(f'{width}x{height}')
        self.screen.title(title)
        

    def add_checkbox(self, text, true_command=None, false_command=None, pack=True, size=(), coord=()) -> "tuple[UUID, BooleanVar]":
        id,variable = self._create_form_content(Content_type.CHECKBOX, text, size, coord, pack, true_command=true_command, false_command=false_command)
        return id, variable

    def add_button(self, text, command, pack=True, size=(), coord=()) -> UUID:
        ''' create a "button", if to be packed, packed = True.
        @return id of the widget'''
        id, _ = self.widget_maker._create_form_content(Content_type.BUTTON, text, size, coord, pack, command=command)
        return id 

    def add_label(self, text, pack=True, size=(), coord=()) -> UUID:
        ''' create a "label" widget, if to be packed, packed = True.
        @return id of the widget'''
        id, _ = self.widget_maker._create_form_content(Content_type.LABEL, text, size, coord, pack)
        return id

    def add_text(self, text, pack=True, size=(), coord=())-> tuple:
        ''' create a "text" widget, 
        Text widget is more advanced than Entry Widget and will wrap text
        if to be packed, packed = True.
        @return id of the widget'''
        id, var = self.widget_maker._create_form_content(Content_type.TEXT, text, size, coord, pack)
        return id, var
        
    def add_entry(self, text, pack=True, size=(), coord=())-> tuple:
        ''' create an "entry" widget, if to be packed, packed = True.
        Entry widget is more limited than entry widget. better for short input
        @return id of the widget and the variable'''
        id, var = self.widget_maker._create_form_content(Content_type.ENTRY, text, size, coord, pack)
        return id, var

    def add_option_menu(self, text, options: list, pack=True, size=(), coord=()) -> "tuple[UUID, StringVar]":
        ''' create an "option" widget, 
        @param options: list of options for user to chose. Must be list of strings
        @return id of the widget and the variable created'''
        id, var = self.widget_maker._create_form_content(Content_type.OPTIONS, text, size, coord, pack, options=options)
        return id, var

    ''' === methods to change widgets === '''

    def enable(self, id):
        for item in self.widget_maker.contents[id]:
            item.config(state=NORMAL)

    def disable(self, id):
        for item in self.widget_maker.contents[id]:
            item.config(state=DISABLED)

    def toggle(self, id):
        for item in self.widget_maker.contents[id]:
            if str(item['state']).lower() == 'normal': item.config(state=DISABLED)
            else: item.confit(state=NORMAL)

    def clear(self, id):
        widget_name = ''
        try:
            for widget in self.widget_maker.contents[id]:
                widget_name = str(type(widget))
                if not isinstance(widget,Label): widget.delete('1.0','end') 
        except Exception as e: print(f'cant clear {widget_name}' )

    def clear_all(self):
        widget_name = ''
        for widget_list in list(self.widget_maker.contents.values()):
            for widget in widget_list: 
                if not isinstance(widget, Label):
                    widget_name = str(type(widget))
                    val = '1.0' if isinstance(widget, Text) else 0
                    try: widget.delete(val,'end')
                    except Exception as e: print(f'cant clear {widget_name}')


    def bind(self, key, command):
        self.screen.bind(key, func=command)

    def message_box(self, message:str, title=''):

        mb.showerror(title=title, message=message.ljust(max(len(title) + 15, len(message))))

    def clear_info(self):
        for label in self.info: label.destroy()
        self.info = []

    def show_info(self, info, replace_info = True):
        ''' show info message at the bottom of the screen 
        @param replace_info : if true, the old info will be written over. else the new will be appended'''
        if replace_info: self.clear_info()
        self.info.append(Label(text=info))
        for label in self.info: label.pack(side=tk.BOTTOM)

    def start_progress_bar(self): # dont work well
        self.progress = ttk.Progressbar(self.screen, orient='horizontal', mode='indeterminate', maximum=100)
        self.progress.pack()
        self.screen.update()
        self.progress.start()
        self.progress.step(5)

    def stop_progress_bar(self): # dont work well
        if not 'self.progress' in locals(): 
            print('problem')
            return
        self.progress.destroy()

    def mainloop(self):
        ''' run mainloop of the screen '''
        self.screen.mainloop()


    ''' === methods for private use only === '''


class Widget_Maker:
    
    def __init__(self, screen):
        self.screen = screen
        self.contents = {}
    
    def _create_form_content(self, widget_type, text, size=(), coord=(), pack=True, options=[], command=None, true_command=None, false_command=None):
        ''' internal use to create the widgets and return their id and variables if applicable '''
        if size != (): width,height = size
        else: width,height = len(text) + 5, 1

        create = {
            Content_type.BUTTON: lambda : self._create_btn(text, height, width, command),
            Content_type.ENTRY: lambda : self._create_entry(text, height, width),
            Content_type.LABEL: lambda : self._create_label(text, height, width),
            Content_type.TEXT: lambda : self._create_text(text, height, width),
            Content_type.OPTIONS: lambda : self._create_option_menu(text, options),
            Content_type.CHECKBOX: lambda: self._create_checkbox(text, height, width, true_command, false_command)
            }
        create_widget = create[widget_type]
        variable, widgets = create_widget()
        id = uuid.uuid1()
        self.contents[id] = widgets
        for widget in widgets: widget.pack()
        return id, variable

    def _create_option_menu(self, text, options:"list[str]") -> tuple:
        ''' create an option menu and fill with list of options
        @param the text of associated label if not string or empty, no label is created
        @param options: the list of options to drop down. must be list of string
        @return the tuple of variable and the list of widgets
        '''
        content_list = []
        if not isinstance(text, str) and len(text) > 0: content_list.append(Label(self.screen, text=text))
        var = StringVar()
        var.set('choose an option')
        option_widget = OptionMenu(self.screen, var, *options)
        content_list.append(option_widget)
        return var, content_list

    def _create_btn(self, text, height, width, command) -> tuple:
        ''' create button and return in list. 
        No variable so return None as 1st element in tuple '''
        if command==None: 
            print('no command specified')
            return None, None 
        obj = Button(self.screen, text=text, command=command)
        obj.configure(height=height, width=width)
        return None, [obj]

    def _create_label(self, text, height, width) -> tuple:
        '''create label and return in list.
        No variable so return None as 1st element in tuple'''
        obj = Label(self.screen, text=text)
        obj.configure(height=height, width=width)
        return None, [obj]

    def _create_entry(self, text, height, width) -> "tuple[StringVar, list]":
        '''create an "entry" widget
        @return tuple: stringVar of this entry and list containing the objects created - a label and the entry'''
        var = StringVar()
        label = Label(self.screen, text=text,)
        obj = Entry(self.screen, textvariable=var)
        obj.configure(width=width)
        return var,[label,obj]

    def _create_text(self, text, height, width) -> "tuple[TextWrapper, list]":
        ''' create a "text" widget. 
        @param the text of associated label if not string or empty, no label is created
        @return tuple: stringVar of this entry and list containing the objects created - a label and a TextWrapper for accessing the variable'''
        content_list = []
        if isinstance(text, str) and len(text) > 0 : content_list.append(Label(self.screen, text=text))
        text_widget = Text(self.screen, wrap=WORD)
        text_widget.configure(height=height, width=width)
        content_list.append(text_widget)
        var = TextWrapper(text_widget)
        print(content_list)
        return var, content_list

    def _create_checkbox(self, text, height, width, true_command, false_command):
        var = tk.BooleanVar(value=True)

        def fn():
            print(var.get())
            if var.get(): true_command()
            else: false_command()

        checkbox = tk.Checkbutton(self.screen, text=text, variable=var, onvalue=True, offvalue=False, command=fn, )
        checkbox.pack()
        return var, [checkbox]
    
    
parent = Form(500,200, 'parent')

# def generate_child(parent):
#     child = parent.generate_child(300,300, 'child')
#     child.mainloop()
    
# parent.add_button('generate child', command=lambda : generate_child(parent))
parent.mainloop()