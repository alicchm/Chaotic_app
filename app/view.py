import tkinter as tk
from tkinter import CENTER, LEFT, RIGHT, Toplevel, ttk, filedialog
from PIL import ImageTk, Image, ImageStat
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from io import BytesIO
import win32clipboard, os
from datetime import datetime
from controller import Controller
from tkinter.messagebox import showinfo, showerror
from tkinter.font import Font
import copy
import ctypes

class View():
    def __init__(self, master):
        # ctypes.windll.shcore.SetProcessDpiAwareness(1)

        self.root = master
        self.root.protocol("WM_DELETE_WINDOW", self.app_close)
        self.controller = None

        #zmienne
        self.path = None
        self.image = None
        self.image_toview = None
        self.cipher_type = 1
        #self.enc_image = None
        #self.enc_image_tk = None
        self.cryptogram = None
        self.cryptogram_toview = None
        #self.image_todecrypt = None
        self.image_decrypted = None
        self.image_decrypted_toview = None
        self.x = None
        self.p = None
        self.spx = None

        #miary
        self.key_sensivity = None
        self.npcr = None
        self.uaci = None
        self.entropy = None
        self.get_correlations = None

        #rozmiary okien, obrazów itp.
        self.root_window_width = 820
        self.root_window_height = 497 
        self.small_window_width = 816 
        self.small_window_height = 472
        self.nb_page_width = 816 
        self.nb_page_height = 467 
        self.max_image_width = 350 
        self.max_image_height = 350 

        #scieżki do obrazów w tle, logo, tytuł okien
        self.main_encode_bg = 'bg_img/encode_bg2.png'
        self.main_decode_bg = 'bg_img/decode_bg2.png'
        self.encoded_window_bg1 = 'bg_img/encoded_window_bg2.png'
        self.encoded_window_bg2 = 'bg_img/encoded_measures_bg222.png'
        self.decoded_window_bg = 'bg_img/decoded_window_bg2.png'
        self.copy_text_img = 'bg_img/copy_symbol2.png'

        self.logo_img = 'app_logo_mini2.png'
        self.window_title = 'Chaotyczne szyfrowanie obrazów'

        #paleta kolorów
        self.dark_bg_color = "#242424"
        self.offwhite_color = "#f5f5f5"
        self.white_color = "#ffffff"
        self.orange_color = "#e59500"
        self.light_orange_color = "#FFC969"
        self.dark_gray_color = "#93A295"
        self.light_gray_color = "#CED4CF"

        #właściwości głównego okna
        self.root.geometry(f'{self.root_window_width}x{self.root_window_height}')
        self.root.title(self.window_title)
        self.root.configure(bg=self.dark_bg_color)
        self.root.resizable(False, False) 

        self.root_icon = ImageTk.PhotoImage(file = self.logo_img)
        self.root.iconphoto(False, self.root_icon)

        #notebook = tworzenie zakładek
        self.enc_style_notebook = ttk.Style()
        self.enc_style_notebook.theme_use('clam')
        self.enc_style_notebook.configure('TNotebook.Tab', background=self.offwhite_color)
        self.enc_style_notebook.configure('TNotebook', background=self.dark_bg_color, bordercolor=self.dark_bg_color)
        self.enc_style_notebook.map("TNotebook.Tab", background= [('selected', self.dark_bg_color)], foreground=[('selected',self.white_color)])

        self.notebook = ttk.Notebook(self.root, style='TNotebook')
        self.notebook.grid(column=0, row=0)

        #tworzenie zakładek i dodanie ich do notebooka
        self.page_encode = tk.Frame(self.notebook, width=self.nb_page_width, height=self.nb_page_height, bg=self.dark_bg_color)
        self.page_decode = tk.Frame(self.notebook, width=self.nb_page_width, height=self.nb_page_height, bg=self.dark_bg_color)
        self.page_description = tk.Frame(self.notebook, width=self.nb_page_width, height=self.nb_page_height, bg=self.dark_bg_color)

        self.page_encode.grid(sticky='NESW')
        self.page_decode.grid(sticky='NESW')
        self.page_description.grid(sticky='NESW')

        self.notebook.bind("<<NotebookTabChanged>>", self.routine)
        self.notebook.bind("<<NotebookTabChanged>>", self.routine)
        #self.page_description.bind("<<NotebookTabChanged>>", self.routine())

        self.notebook.add(self.page_encode, text='Szyfrowanie')
        self.notebook.add(self.page_decode, text='Deszyfrowanie')
        self.notebook.add(self.page_description, text='Opis algorytmów')

        #strona z kodowaniem
        #tło strony
        self.enc_bg_img = ImageTk.PhotoImage(Image.open(self.main_encode_bg))
        self.enc_bgimg_label = tk.Label(self.page_encode, image=self.enc_bg_img, bg=self.dark_bg_color)
        self.enc_bgimg_label.img = self.enc_bg_img  
        self.enc_bgimg_label.place(relx=0.5, rely=0.5, anchor='center')

        #przycisk ładowania obrazu
        self.enc_loadimg_button = tk.Button(self.page_encode, text = 'Ładuj obraz', command=lambda:self.enc_openimage(1), width=15, height=1, bg=self.orange_color, bd=0)
        self.enc_loadimg_button.place(relx=0.086, rely=0.2067)

        #wybór algorytmu
        self.enc_option_radio = tk.IntVar()
        self.enc_style_radiobutton = ttk.Style()
        self.enc_style_radiobutton.configure('enc_radio.TRadiobutton', background=self.orange_color)

        self.enc_algorithm1_radio = ttk.Radiobutton(self.page_encode, text='Algorytm 1.', variable=self.enc_option_radio, value=1, command=lambda:self.enc_selectalgorithm(1), style='enc_radio.TRadiobutton')
        self.enc_algorithm1_radio.place(relx=0.09, rely=0.35)
        
        self.enc_algorithm2_radio = ttk.Radiobutton(self.page_encode, text='Algorytm 2.', variable=self.enc_option_radio, value=2, command=lambda:self.enc_selectalgorithm(2), style='enc_radio.TRadiobutton')
        self.enc_algorithm2_radio.place(relx=0.09, rely=0.4)
        self.enc_option_radio.set(1)

        #wartość x
        self.enc_x = tk.StringVar()
        self.enc_x_before = tk.StringVar()
        self.enc_x_range = ['0.001', '0.999']
        self.enc_x.set(self.enc_x_range[0])
        self.enc_x_before.set(self.enc_x_range[0])

        self.enc_x_label = tk.Label(self.page_encode, text='x =', bg=self.orange_color)
        self.enc_x_label.place(relx=0.091, rely=0.55)

        entry_x_val_function = self.root.register(self.entry_x_validate)
        entry_x_inval_function = self.root.register(self.entry_x_invalid)
        self.enc_x_entry = tk.Entry(self.page_encode, width=10, relief='flat', bd=0, bg=self.light_orange_color, textvariable=self.enc_x, justify=tk.LEFT)
        self.enc_x_entry.config(validate='focusout', validatecommand=(entry_x_val_function,'%P'), invalidcommand=(entry_x_inval_function))
        self.enc_x_entry.place(relx=0.125, rely=0.555)

        #wartość p
        self.enc_p = tk.StringVar()
        self.enc_p_before = tk.StringVar()
        self.enc_p_range = ['0.25', '0.5']
        self.enc_p.set(self.enc_p_range[0])
        self.enc_p_before.set(self.enc_p_range[0])

        self.enc_p_label = tk.Label(self.page_encode, text='p =', bg=self.orange_color)
        self.enc_p_label.place(relx=0.091, rely=0.6)

        entry_p_val_function = self.root.register(self.entry_p_validate)
        entry_p_inval_function = self.root.register(self.entry_p_invalid)
        self.enc_p_entry = tk.Entry(self.page_encode, width=10, relief='flat', bd=0, bg=self.light_orange_color, textvariable=self.enc_p, justify=tk.LEFT)
        self.enc_p_entry.config(validate='focusout', validatecommand=(entry_p_val_function,'%P'), invalidcommand=(entry_p_inval_function))        
        self.enc_p_entry.place(relx=0.125, rely=0.605)

        #szyfrowanie - start algorytmu
        self.enc_encode_button = tk.Button(self.page_encode, text = 'Szyfruj!', width=15, height=1, bg=self.orange_color, bd=0, command=self.start_encryption) #TU BD START ENC
        self.enc_encode_button.place(relx=0.086, rely=0.7398)

        #wyświetlanie załadowanego obrazu
        #w funkcji set_image_for_enc()
        
        #strona z dekodowaniem
        #tło strony
        self.dec_bg_img = ImageTk.PhotoImage(Image.open(self.main_decode_bg))
        self.dec_bgimg_label = tk.Label(self.page_decode, image=self.dec_bg_img, bg=self.dark_bg_color)
        self.dec_bgimg_label.img = self.dec_bg_img  
        self.dec_bgimg_label.place(relx=0.5, rely=0.5, anchor='center')

        #przycisk ładowania obrazu
        self.dec_loadimg_button = tk.Button(self.page_decode, text = 'Ładuj obraz', command=lambda:self.enc_openimage(2), width=15, height=1, bg=self.orange_color, bd=0)
        self.dec_loadimg_button.place(relx=0.086, rely=0.17)

        #wybór algorytmu
        self.dec_option_radio = tk.IntVar()
        self.dec_style_radiobutton = ttk.Style()
        self.dec_style_radiobutton.configure('dec_radio.TRadiobutton', background=self.orange_color)

        self.dec_algorithm1_radio = ttk.Radiobutton(self.page_decode, text='Algorytm 1.', variable=self.dec_option_radio, value=1, command=lambda:self.enc_selectalgorithm(1), style='dec_radio.TRadiobutton')
        self.dec_algorithm1_radio.place(relx=0.09, rely=0.31)

        self.dec_algorithm2_radio = ttk.Radiobutton(self.page_decode, text='Algorytm 2.', variable=self.dec_option_radio, value=2, command=lambda:self.enc_selectalgorithm(2), style='dec_radio.TRadiobutton')
        self.dec_algorithm2_radio.place(relx=0.09, rely=0.36)
        self.dec_option_radio.set(1)

        #wartość x
        self.dec_x_label = tk.Label(self.page_decode, text='x =', bg=self.orange_color)
        self.dec_x_label.place(relx=0.091, rely=0.455)

        entry_x_val_function_dec = self.root.register(self.entry_x_validate_dec)
        entry_x_inval_function_dec = self.root.register(self.entry_x_invalid_dec)
        self.dec_x_entry = tk.Entry(self.page_decode, width=10, relief='flat', bd=0, bg=self.light_orange_color, textvariable=self.enc_x, justify=tk.LEFT)
        self.dec_x_entry.config(validate='focusout', validatecommand=(entry_x_val_function_dec,'%P'), invalidcommand=(entry_x_inval_function_dec))
        self.dec_x_entry.place(relx=0.125, rely=0.46)

        #wartość p
        self.dec_p_label = tk.Label(self.page_decode, text='p =', bg=self.orange_color)
        self.dec_p_label.place(relx=0.091, rely=0.505)

        entry_p_val_function_dec = self.root.register(self.entry_p_validate_dec)
        entry_p_inval_function_dec = self.root.register(self.entry_p_invalid_dec)
        self.dec_p_entry = tk.Entry(self.page_decode, width=10, relief='flat', bd=0, bg=self.light_orange_color, textvariable=self.enc_p, justify=tk.LEFT)
        self.dec_p_entry.config(validate='focusout', validatecommand=(entry_p_val_function_dec,'%P'), invalidcommand=(entry_p_inval_function_dec))        
        self.dec_p_entry.place(relx=0.125, rely=0.51)

        #wartość klucza
        self.dec_key_label = tk.Label(self.page_decode, text='Wartość klucza =', bg=self.orange_color)
        self.dec_key_label.place(relx=0.095, rely=0.595)

        self.dec_key = tk.StringVar()
        self.dec_key_before = tk.StringVar()
        self.dec_key_range = ['0', '1000000000']
        self.dec_key.set(self.dec_key_range[0])
        self.dec_key_before.set(self.dec_key_range[0])

        entry_key_function = self.root.register(self.entry_key_validate)
        entry_key_inval_function = self.root.register(self.entry_key_invalid)
        self.dec_key_entry = tk.Entry(self.page_decode, width=11, relief='flat', bd=0, bg=self.light_orange_color, textvariable=self.dec_key, justify=tk.LEFT)
        self.dec_key_entry.config(validate='focusout', validatecommand=(entry_key_function,'%P'), invalidcommand=(entry_key_inval_function))        
        self.dec_key_entry.place(relx=0.107, rely=0.645)

        #deszyfrowanie - start algorytmu
        self.dec_encode_button = tk.Button(self.page_decode, text = 'Deszyfruj!', width=15, height=1, bg=self.orange_color, bd=0, command=self.start_decryption)
        self.dec_encode_button.place(relx=0.086, rely=0.786)

        #wyświetlanie załadowanego obrazu TERAZ JEST W FUNKCJI set_image_for_dec
        #self.dec_image = Image.open("encoded.png")
        #self.dec_image = self.dec_image.resize(self.resize_image(self.dec_image), Image.Resampling.LANCZOS)
        #self.dec_image_tk = ImageTk.PhotoImage(self.dec_image)

        #self.dec_image_label = ttk.Label(self.page_decode, image=self.dec_image_tk)
        #self.dec_image_label.place(relx=0.425, rely=0.082)

        #strona z opisem algorytmów
        self.desc_main_frame = tk.Frame(self.page_description, bg=self.dark_bg_color)
        self.desc_main_frame.pack(fill='both', expand=1)

        self.desc_canvas = tk.Canvas(self.desc_main_frame, bg=self.dark_bg_color)
        self.desc_canvas.pack(side='left', fill='both', expand=1)

        self.desc_scrollbar = tk.Scrollbar(self.desc_main_frame, orient='vertical', command=self.desc_canvas.yview, bg=self.dark_bg_color)
        self.desc_scrollbar.pack(side='right', fill='y')

        self.desc_canvas.configure(yscrollcommand=self.desc_scrollbar.set)
        self.desc_canvas.bind('<Configure>', lambda e: self.desc_canvas.configure(scrollregion = self.desc_canvas.bbox("all")))

        self.desc_inner_frame = tk.Frame(self.desc_canvas, bg=self.dark_bg_color)
        self.desc_canvas.create_window((0,0), window=self.desc_inner_frame, anchor='nw')

        self.desc_alg1_textbox = tk.Text(self.desc_inner_frame, height=5, bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.desc_alg1_textbox.insert(1.0,'Tutaj może jakiś tekst.\n A tu jeszcze trochę tekstu.')
        self.desc_alg1_textbox.configure(state='disabled')
        self.desc_alg1_textbox.grid(column=0, row=0, sticky='ew')

        self.desc_alg1_label = tk.Label(self.desc_inner_frame, height=5, text='Może tu jakiś wzór', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.desc_alg1_label.grid(column=0, row=1, sticky='ew')

        self.desc_alg2_label = tk.Label(self.desc_inner_frame, height=5, text='Może tu jeszcze jakiś wzór', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.desc_alg2_label.grid(column=0, row=2, sticky='ew')

        self.desc_alg2_textbox = tk.Text(self.desc_inner_frame, height=5, bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.desc_alg2_textbox.insert(1.0,'Tutaj może jakiś tekst.\n A tu jeszcze trochę tekstu.')
        self.desc_alg2_textbox.configure(state='disabled')
        self.desc_alg2_textbox.grid(column=0, row=3, sticky='ew')

        self.desc_alg2_textbox = tk.Text(self.desc_inner_frame, height=5, bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.desc_alg2_textbox.insert(1.0,'Tutaj może jakiś tekst.\n A tu jeszcze trochę tekstu.')
        self.desc_alg2_textbox.configure(state='disabled')
        self.desc_alg2_textbox.grid(column=0, row=4, sticky='ew')

    def routine(self, event):
        self.path = None
        self.image = None
        self.encrypted_image = None
        self.image_todecrypt = None
        self.image_decrypted = None
        self.x = None
        self.p = None
        self.spx = None
        self.cipher_type = 1
        self.enc_x.set(self.enc_x_range[0])
        self.enc_p.set(self.enc_p_range[0])
        self.enc_x_before.set(self.enc_x_range[0])
        self.enc_p_before.set(self.enc_p_range[0])
        self.dec_key.set(self.dec_key_range[0])
        print('działa')
        self.enc_option_radio.set(1)
        self.dec_option_radio.set(1)
        if hasattr(self, 'enc_image_label'):
            self.enc_image_label.config(image='')
            print('działa 1')

        if hasattr(self, 'dec_image_label'):
            self.dec_image_label.config(image='')
            print('działa 2')

    def setController(self, controller):
        self.controller = controller

    def enc_openimage(self, tab_num):
        enc_filename = filedialog.askopenfilename(
            title = 'Wybierz obraz',
            filetypes=[('Obraz JPG','*.jpg')]
        )

        # showinfo(title='Wybrany plik', message=f'{enc_filename},{type(enc_filename)}')
        if enc_filename != '':
            if Image.open(enc_filename).mode == 'RGB':
                # showinfo(title='Wybrany plik', message=Image.open(enc_filename).mode)
                #USTAWIANIE ŚCIEŻKI I OBRAZU
                self.path = enc_filename
                self.controller.set_image(self.path)
                #TUTAJ SIE USTAWIA OBRAZEK JAKĄŚ FUNKCJĄ FOR EXAMPLE self.controller.get_image()
                
                if tab_num == 1:
                    self.image = self.controller.get_image().copy()
                    self.set_image_for_enc()
                else:
                    self.image = self.controller.get_image().copy()
                    self.set_image_for_dec()
            else:
                msg = 'Wybrano nieobsługiwany typ pliku. Wymagany model przestrzeni barw obrazu to RGB (model RGBA nie jest obsługiwany).'
                showerror(title='Nieobsługiwany plik', message=msg)

    def check_if_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def check_if_int(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def entry_x_validate(self, value): #walidacja wprowadzonej wartości x
        if value != '' and self.check_if_float(value) == True:
            val_float = float(value)
            #TU JESZCZE SPRAWDZENIE CZY JEST W ODPOWIEDNIM ZAKRESIE
            self.enc_x.set(val_float)
            self.enc_x_before.set(val_float)
            return True
        else:       
            return False

    def entry_x_validate_dec(self, value): #walidacja wprowadzonej wartości x
        print('x decode val')
        if value != '' and self.check_if_float(value) == True:
            val_float = float(value)
            #TU JESZCZE SPRAWDZENIE CZY JEST W ODPOWIEDNIM ZAKRESIE
            self.enc_x.set(val_float)
            self.enc_x_before.set(val_float)
            return True
        else:       
            return False

    def entry_x_invalid(self):  #instrukcja dla niepoprawnie wprowadzonej wartości x
        msg = f'Podana wartość jest nieprawidłowa. Podaj liczbę dziesiętną z przedziału (0,1). Miejsca dziesiętne oddziel od całości kropką.'
        showerror(title='Niepoprawna wartość', message=msg)
        
        self.enc_x_entry.delete(0,tk.END)
        self.enc_x_entry.insert(0,float(self.enc_x_before.get()))
        self.enc_x.set(self.enc_x_before.get())

    def entry_x_invalid_dec(self):  #instrukcja dla niepoprawnie wprowadzonej wartości x
        print('x decode inval')
        msg = f'Podana wartość jest nieprawidłowa. Podaj liczbę dziesiętną z przedziału (0,1). Miejsca dziesiętne oddziel od całości kropką.'
        showerror(title='Niepoprawna wartość', message=msg)
        
        self.dec_x_entry.delete(0,tk.END)
        self.dec_x_entry.insert(0,float(self.enc_x_before.get()))
        self.enc_x.set(self.enc_x_before.get())

    def entry_p_validate(self, value): #walidacja wprowadzonej wartości p
        if value != '' and self.check_if_float(value) == True:
            val_float = float(value)
            if (val_float<=0.5 and val_float>=0.25 and self.enc_option_radio.get()==1) or (val_float<1 and val_float>0 and self.enc_option_radio.get()==2):
                self.enc_p.set(val_float)
                self.enc_p_before.set(val_float)
                return True
            else: 
                return False
        else:      
            return False

    def entry_p_validate_dec(self, value): #walidacja wprowadzonej wartości p
        print('p decode val')
        if value != '' and self.check_if_float(value) == True:
            val_float = float(value)
            if (val_float<=0.5 and val_float>=0.25 and self.dec_option_radio.get()==1) or (val_float<1 and val_float>0 and self.dec_option_radio.get()==2):
                self.enc_p.set(val_float)
                self.enc_p_before.set(val_float)
                return True
            else: 
                return False
        else:      
            return False

    def entry_p_invalid(self):  #instrukcja dla niepoprawnie wprowadzonej wartości p
        range = ''
        if self.enc_option_radio.get() == 1:
            range = f'[0.25, 0.5]'
        else:
            range = f'(0, 1)'
        msg = f'Podana wartość jest nieprawidłowa. Podaj liczbę dziesiętną z przedziału {range}. Miejsca dziesiętne oddziel od całości kropką.'
        showerror(title='Niepoprawna wartość', message=msg)
        
        self.enc_p_entry.delete(0,tk.END)
        self.enc_p_entry.insert(0,float(self.enc_p_before.get()))

        self.enc_p.set(self.enc_p_before.get())
    
    def entry_p_invalid_dec(self):  #instrukcja dla niepoprawnie wprowadzonej wartości p
        print('p decode inval')
        range = ''
        if self.dec_option_radio.get() == 1:
            range = f'[0.25, 0.5]'
        else:
            range = f'(0, 1)'
        msg = f'Podana wartość jest nieprawidłowa. Podaj liczbę dziesiętną z przedziału {range}. Miejsca dziesiętne oddziel od całości kropką.'
        showerror(title='Niepoprawna wartość', message=msg)
        
        self.dec_p_entry.delete(0,tk.END)
        self.dec_p_entry.insert(0,float(self.enc_p_before.get()))

        self.enc_p.set(self.enc_p_before.get())

    def entry_key_validate(self, value): #walidacja wprowadzonej wartości klucza
        if value != '' and self.check_if_int(value) == True:
            val_int = int(value)
            if val_int>=0:
                self.dec_key.set(val_int)
                self.dec_key_before.set(val_int)
                return True
            else:
                return False
        else:      
            return False

    def entry_key_invalid(self):  #instrukcja dla niepoprawnie wprowadzonej wartości klucza
        msg = f'Podana wartość jest nieprawidłowa. Podaj nieujemną liczbę całkowitą.'
        showerror(title='Niepoprawna wartość', message=msg)
        
        self.dec_key_entry.delete(0,tk.END)
        self.dec_key_entry.insert(0,int(self.dec_key_before.get()))

        self.dec_key.set(self.dec_key_before.get())

    def save_img(self, parent_window, img, tab_number):
        file_dir = filedialog.askdirectory(
            initialdir=os.getcwd(), 
            title='Zapisz plik',
            parent=parent_window)

        if file_dir!='' and self.path!=None: #and spx!=none
            file_type = self.path.split('.')[1]
            full_path = ''
            if tab_number == 1: #zapisywanie zakodowanego obrazu
                full_path = f'{file_dir}/encoded_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{self.controller.get_Spx()}.{file_type}'
                showinfo(title='Wybrany plik', message=full_path)
            elif tab_number == 2:   #zapisywanie odkodowanego obrazu 
                full_path = f'{file_dir}/decoded_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{file_type}'
                showinfo(title='Wybrany plik', message=full_path)
            img.save(full_path, format='PNG', subsampling=0, quality=100)

        parent_window.focus_set()   #żeby podrzędne okno było dalej na wierzchu

    def resize_image(self, img):
        width, height = img.size
        if width>self.max_image_width or height>self.max_image_height:
            if width>height:
                if width>self.max_image_width:
                    height = (height*self.max_image_width)/width
                    width = self.max_image_width
            else:
                width = (width*self.max_image_height)/height
                height = self.max_image_height

        return int(width), int(height)

    def enc_selectalgorithm(self, cipher_type):
        print('wybrano algorytm: ', self.enc_option_radio.get())
        if self.enc_option_radio.get() == 1:
            self.enc_p_range[0] = '0.25'
            self.enc_p_range[1] = '0.5'
            self.enc_x_range[0] = '0.001'
            self.enc_x_range[1] = '0.999'
        elif self.enc_option_radio.get() == 2:
            self.enc_p_range[0] = '0.001'
            self.enc_p_range[1] = '0.999'
            self.enc_x_range[0] = '0.001'
            self.enc_x_range[1] = '0.999'

        self.enc_p.set(self.enc_p_range[0])
        self.enc_p_before.set(self.enc_p_range[0])
        self.enc_x.set(self.enc_x_range[0])
        self.enc_x_before.set(self.enc_x_range[0])
        
        self.cipher_type = cipher_type

    def app_close(self):
        self.root.quit()
        self.root.destroy()

    def inner_window_close(self, win):
        win.destroy()

    def enc_open_window(self):
        enc2_window = Toplevel(self.root)
        enc2_window.geometry(f'{self.small_window_width}x{self.small_window_height}')
        enc2_window.title(self.window_title)
        enc2_window.configure(bg=self.dark_bg_color)
        enc2_window.resizable(False, False)
        enc2_window.protocol("WM_DELETE_WINDOW", lambda: self.inner_window_close(enc2_window))

        enc2_window_icon = ImageTk.PhotoImage(file = self.logo_img)
        enc2_window.iconphoto(False, enc2_window_icon)

        #strona z zakodowanym obrazem
        page2_encode_results = tk.Frame(enc2_window, width=self.nb_page_width, height=self.nb_page_height, bg=self.dark_bg_color)
        page2_encode_results.grid(column=0, row=0, sticky='news')

        #tło strony
        enc2_bg_img = ImageTk.PhotoImage(Image.open(self.encoded_window_bg1))
        enc2_bgimg_label = tk.Label(page2_encode_results, image=enc2_bg_img, bg=self.dark_bg_color)
        enc2_bgimg_label.img = enc2_bg_img  
        enc2_bgimg_label.place(relx=0.5, rely=0.5, anchor='center')
        
        #wyświetlenie zakodowanego obrazu
        #TU MOŻNA Z PALCA ZROBIĆ JAK W FUNKACJACH ŁADUJĄCYCH OBRAZY PRZYPISZE SIĘ ZMIENNĄ
        #nc2_img_base = Image.open("encoded.png") #self.encrypted_image
        self.cryptogram_toview = copy.copy(self.cryptogram)
        enc2_img = ImageTk.PhotoImage(self.cryptogram_toview.resize(self.resize_image(self.cryptogram_toview), Image.Resampling.LANCZOS))
        enc2_img_label = tk.Label(page2_encode_results, image=enc2_img)
        enc2_img_label.img = enc2_img  
        enc2_img_label.place(relx=0.29, rely=0.5, anchor='center')

        #button - zapisz obraz
        enc2_save_button = tk.Button(page2_encode_results, text = 'Zapisz obraz', width=15, height=1, bg=self.dark_gray_color, bd=0, command=lambda:self.save_img(enc2_window, self.cryptogram, 1))
        enc2_save_button.place(relx=0.777, rely=0.219)

        #button - kopiuj obraz do schowka
        enc2_copy_button = tk.Button(page2_encode_results, text = 'Kopiuj obraz', width=15, height=1, bg=self.dark_gray_color, bd=0, command=lambda:self.copy_to_clipboard(self.cryptogram))
        enc2_copy_button.place(relx=0.777, rely=0.35)

        #label - klucz
        enc2_key_label = tk.Label(page2_encode_results, text='Wartość klucza =', bg=self.dark_gray_color, width=15, justify=CENTER)
        enc2_key_label.place(relx=0.777, rely=0.49)

        #label - wartość klucza
        enc2_keyval_label = tk.Text(page2_encode_results, bg=self.light_gray_color, height=1, width=10, relief='flat', inactiveselectbackground=self.light_gray_color)
        enc2_keyval_label.insert(1.0, self.spx)
        enc2_keyval_label.configure(state='disabled') #trzeba najpierw podać zawartość, potem zmienić stan
        enc2_keyval_label.place(relx=0.779, rely=0.54)

        enc2_copy_key_button_img = Image.open(self.copy_text_img).resize((15,15),resample=Image.LANCZOS)
        enc2_copy_key_button_photo = ImageTk.PhotoImage(enc2_copy_key_button_img)
        enc2_copy_key_button = ttk.Button(page2_encode_results, image=enc2_copy_key_button_photo, command=lambda:self.copy_text_to_clipboard(self.spx), width=1, padding='1 1 1 1')
        enc2_copy_key_button.place(relx=0.883, rely=0.535)
        enc2_copy_key_button.image = enc2_copy_key_button_photo

        #strona z miarami jakości
        page2_encode_measures = tk.Frame(enc2_window, width=self.nb_page_width, height=self.nb_page_height, bg=self.dark_bg_color)
        page2_encode_measures.grid(column=0, row=0, sticky='news')
        
        #tło strony
        enc2_meas_bg_img = ImageTk.PhotoImage(Image.open(self.encoded_window_bg2))
        enc2_meas_bgimg_label = tk.Label(page2_encode_measures, image=enc2_meas_bg_img, bg=self.dark_bg_color)
        enc2_meas_bgimg_label.img = enc2_meas_bg_img  
        enc2_meas_bgimg_label.place(relx=0.5, rely=0.5, anchor='center')

        #button - do wyników kodowania
        enc2_toresults_button = tk.Button(page2_encode_measures, text = 'Powrót', width=20, height=1, bg=self.light_gray_color, bd=0, command=lambda: self.change_frame(page2_encode_results))
        enc2_toresults_button.place(relx=0.029, rely=0.905)

        #ramka z wynikami miar jakości
        enc2_outer_measure_frame = tk.Frame(page2_encode_measures, width=(self.nb_page_width-48), height=(self.nb_page_height-108), bg=self.dark_bg_color)
        enc2_outer_measure_frame.place(relx=0.5, rely=0.049, anchor='n')

        measure_main_frame = tk.Frame(enc2_outer_measure_frame, width=(self.nb_page_width-48), height=(self.nb_page_height-108), bg=self.dark_bg_color)
        measure_main_frame.pack(fill='both', expand=1)

        measure_canvas = tk.Canvas(measure_main_frame, width=(self.nb_page_width-48), height=(self.nb_page_height-108), bg=self.dark_bg_color)
        measure_canvas.pack(side='left', fill='both', expand=1)

        measure_scrollbar = tk.Scrollbar(measure_main_frame, orient='vertical', command=measure_canvas.yview, bg=self.dark_bg_color)
        measure_scrollbar.pack(side='right', fill='y')

        measure_canvas.configure(yscrollcommand=measure_scrollbar.set)
        measure_canvas.bind('<Configure>', lambda e: measure_canvas.configure(scrollregion = measure_canvas.bbox("all")))

        measure_inner_frame = tk.Frame(measure_canvas, bg=self.dark_bg_color)
        measure_canvas.create_window((0,0), window=measure_inner_frame, anchor='nw')

        #poszczególne widgety z wynikami miar jakości
        #histogramy
        measure_label_hist = tk.Label(measure_inner_frame, height=5, text='Histogramy', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        measure_label_hist.grid(column=0, row=0, sticky='ew')

        fig_hist1 = Figure(figsize=(4.25,3), dpi=60)
        canvas_hist1 = FigureCanvasTkAgg(fig_hist1, measure_inner_frame)
        canvas_hist1.get_tk_widget().grid(column=0,row=1)

        fig_hist2 = Figure(figsize=(4.25,3), dpi=60) 
        canvas_hist2 = FigureCanvasTkAgg(fig_hist2, measure_inner_frame)
        canvas_hist2.get_tk_widget().grid(column=1,row=1)

        fig_hist3 = Figure(figsize=(4.25,3), dpi=60)
        canvas_hist3 = FigureCanvasTkAgg(fig_hist3, measure_inner_frame)
        canvas_hist3.get_tk_widget().grid(column=2,row=1)

        #npcr
        measure_label_npcr = tk.Label(measure_inner_frame, height=5, text='NPCR', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        measure_label_npcr.grid(column=0, row=2, sticky='ew')

        self.npcr_r_label = tk.Label(measure_inner_frame, height=1, text='R: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.npcr_r_label.grid(column=0, row=3)

        self.npcr_g_label = tk.Label(measure_inner_frame, height=1, text='G: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.npcr_g_label.grid(column=1, row=3)

        self.npcr_b_label = tk.Label(measure_inner_frame, height=1, text='B: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.npcr_b_label.grid(column=2, row=3)

        #uaci
        measure_label_uaci = tk.Label(measure_inner_frame, height=5, text='UACI', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        measure_label_uaci.grid(column=0, row=4, sticky='ew')

        self.uaci_r_label = tk.Label(measure_inner_frame, height=1, text='R: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.uaci_r_label.grid(column=0, row=5)

        self.uaci_g_label = tk.Label(measure_inner_frame, height=1, text='G: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.uaci_g_label.grid(column=1, row=5)

        self.uaci_b_label = tk.Label(measure_inner_frame, height=1, text='B: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.uaci_b_label.grid(column=2, row=5)

        #entropia
        measure_label_entropy = tk.Label(measure_inner_frame, height=5, text='Entropia', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        measure_label_entropy.grid(column=0, row=6, sticky='ew')

        self.entropy_r_label = tk.Label(measure_inner_frame, height=1, text='R: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.entropy_r_label.grid(column=0, row=7)

        self.entropy_g_label = tk.Label(measure_inner_frame, height=1, text='G: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.entropy_g_label.grid(column=1, row=7)

        self.entropy_b_label = tk.Label(measure_inner_frame, height=1, text='B: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.entropy_b_label.grid(column=2, row=7)

        #key sensitivity
        measure_label_keysens = tk.Label(measure_inner_frame, height=5, text='Key Sensitivity', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        measure_label_keysens.grid(column=0, row=8, sticky='ew')

        self.key_sens1 = Figure(figsize=(4.25,3), dpi=60)
        self.ax1 = self.key_sens1.add_subplot(111)
        self.canvas_sens1 = FigureCanvasTkAgg(self.key_sens1, measure_inner_frame)
        self.canvas_sens1.get_tk_widget().grid(column=0,row=9)

        self.key_sens2 = Figure(figsize=(4.25,3), dpi=60) #(figsize=(5,3), dpi=80)
        self.ax2 = self.key_sens2.add_subplot(111)
        self.canvas_sens2 = FigureCanvasTkAgg(self.key_sens2, measure_inner_frame)
        self.canvas_sens2.get_tk_widget().grid(column=1,row=9)

        self.key_sens3 = Figure(figsize=(4.25,3), dpi=60)
        self.ax3 = self.key_sens3.add_subplot(111)
        self.canvas_sens3 = FigureCanvasTkAgg(self.key_sens3, measure_inner_frame)
        self.canvas_sens3.get_tk_widget().grid(column=2,row=9)

        #korelacja
        measure_label_cor = tk.Label(measure_inner_frame, height=3, text='Korelacja', anchor='sw', bg=self.dark_bg_color, foreground=self.offwhite_color)
        measure_label_cor.grid(column=0, row=10, sticky='ew')

        #horyzontalna
        measure_label_cor_horiz = tk.Label(measure_inner_frame, height=3, text='Horyzontalna', anchor='s', bg=self.dark_bg_color, foreground=self.offwhite_color)
        measure_label_cor_horiz.grid(column=1, row=11, sticky='ew')

        self.corr_r_label_horiz = tk.Label(measure_inner_frame, height=1, text='R: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.corr_r_label_horiz.grid(column=0, row=12)

        self.corr_g_label_horiz = tk.Label(measure_inner_frame, height=1, text='G: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.corr_g_label_horiz.grid(column=1, row=12)

        self.corr_b_label_horiz = tk.Label(measure_inner_frame, height=1, text='B: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.corr_b_label_horiz.grid(column=2, row=12)

        #wertykalna
        measure_label_cor_ver = tk.Label(measure_inner_frame, height=3, text='Wertykalna', anchor='s', bg=self.dark_bg_color, foreground=self.offwhite_color)
        measure_label_cor_ver.grid(column=1, row=13, sticky='ew')

        self.corr_r_label_ver = tk.Label(measure_inner_frame, height=1, text='R: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.corr_r_label_ver.grid(column=0, row=14)

        self.corr_g_label_ver = tk.Label(measure_inner_frame, height=1, text='G: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.corr_g_label_ver.grid(column=1, row=14)

        self.corr_b_label_ver = tk.Label(measure_inner_frame, height=1, text='B: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.corr_b_label_ver.grid(column=2, row=14)

        #diagonalna
        measure_label_cor_dia = tk.Label(measure_inner_frame, height=3, text='Diagonalna', anchor='s', bg=self.dark_bg_color, foreground=self.offwhite_color)
        measure_label_cor_dia.grid(column=1, row=15, sticky='ew')

        self.corr_r_label_dia = tk.Label(measure_inner_frame, height=1, text='R: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.corr_r_label_dia.grid(column=0, row=16)

        self.corr_g_label_dia = tk.Label(measure_inner_frame, height=1, text='G: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.corr_g_label_dia.grid(column=1, row=16)

        self.corr_b_label_dia = tk.Label(measure_inner_frame, height=1, text='B: ', anchor='w', bg=self.dark_bg_color, foreground=self.offwhite_color)
        self.corr_b_label_dia.grid(column=2, row=16)  

        #pusty label
        measure_label_empty = tk.Label(measure_inner_frame, height=3, text=' ', anchor='s', bg=self.dark_bg_color, foreground=self.offwhite_color)
        measure_label_empty.grid(column=1, row=17, sticky='ew')       

        #button - do strony z miarami jakości
        enc2_tomeasures_button = tk.Button(page2_encode_results, text = 'Miary', width=20, height=1, bg=self.light_gray_color, bd=0, command=lambda: self.change_frame_calc(page2_encode_measures, fig_hist1, canvas_hist1, fig_hist2, canvas_hist2, fig_hist3, canvas_hist3)) #
        enc2_tomeasures_button.place(relx=0.878, rely=0.929, anchor='center')

        self.change_frame(page2_encode_results) #żeby na starcie była otwarta pierwsza strona

    def change_frame(self, frame):
        frame.tkraise()

    def change_frame_calc(self, frame, fig_hist1, canvas_hist1, fig_hist2, canvas_hist2, fig_hist3, canvas_hist3):
        self.change_frame(frame)
        self.get_measures()

        #paleta kolorów dla wyników
        red = '#d62728'
        green = '#2ca02c'
        blue = '#1f77b4'

        #obliczenie miar itp
        #histogramy
        self.draw_histograms(copy.copy(self.cryptogram), fig_hist1, canvas_hist1, fig_hist2, canvas_hist2, fig_hist3, canvas_hist3)

        #npcr
        self.npcr_r_label.config(text=f'R: {self.npcr[0]} %', fg=red)
        self.npcr_g_label.config(text=f'G: {self.npcr[1]} %', fg=green)
        self.npcr_b_label.config(text=f'B: {self.npcr[2]} %', fg=blue)

        #uaci
        self.uaci_r_label.config(text=f'R: {self.uaci[0]} %', fg=red)
        self.uaci_g_label.config(text=f'G: {self.uaci[1]} %', fg=green)
        self.uaci_b_label.config(text=f'B: {self.uaci[2]} %', fg=blue)

        #entropia
        self.entropy_r_label.config(text=f'R: {self.entropy[0]}', fg=red)
        self.entropy_g_label.config(text=f'G: {self.entropy[1]}', fg=green)
        self.entropy_b_label.config(text=f'B: {self.entropy[2]}', fg=blue)

        #keysensitivity
        self.key_sensitivity()

        #korelacja
        #horyzontalna
        self.corr_r_label_horiz.config(text=f'R: {self.correlations[0][0]}', fg=red)
        self.corr_g_label_horiz.config(text=f'G: {self.correlations[0][1]}', fg=green)
        self.corr_b_label_horiz.config(text=f'B: {self.correlations[0][2]}', fg=blue)

        #wertykalna
        self.corr_r_label_ver.config(text=f'R: {self.correlations[1][0]}', fg=red)
        self.corr_g_label_ver.config(text=f'G: {self.correlations[1][1]}', fg=green)
        self.corr_b_label_ver.config(text=f'B: {self.correlations[1][2]}', fg=blue)

        #diagonalna
        self.corr_r_label_dia.config(text=f'R: {self.correlations[2][0]}', fg=red)
        self.corr_g_label_dia.config(text=f'G: {self.correlations[2][1]}', fg=green)
        self.corr_b_label_dia.config(text=f'B: {self.correlations[2][2]}', fg=blue)


    def copy_to_clipboard(self, image1): #kopiowanie obrazu do schowka
        output = BytesIO()
        image1.convert("RGB").save(output, "BMP", quality=100, subsampling=0)
        data = output.getvalue()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

    def copy_text_to_clipboard(self, text):
        text = str(text)
        print(text)
        text = text.encode('utf8')
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()

    def dec_open_window(self):
        dec2_window = Toplevel(self.root)
        dec2_window.geometry(f'{self.small_window_width}x{self.small_window_height}')
        dec2_window.title(self.window_title)
        dec2_window.configure(bg=self.dark_bg_color)
        dec2_window.resizable(False, False)
        dec2_window.protocol("WM_DELETE_WINDOW", lambda: self.inner_window_close(dec2_window))

        dec2_window_icon = ImageTk.PhotoImage(file = self.logo_img)
        dec2_window.iconphoto(False, dec2_window_icon)

        #tło strony
        dec2_bg_img = ImageTk.PhotoImage(Image.open(self.decoded_window_bg))
        dec2_bgimg_label = tk.Label(dec2_window, image=dec2_bg_img, bg=self.dark_bg_color)
        dec2_bgimg_label.img = dec2_bg_img  
        dec2_bgimg_label.place(relx=0.5, rely=0.5, anchor='center')

        #wyświetlenie odkodowanego obrazu
        #dec2_img_base = Image.open("lena.jpg")
        self.image_decrypted_toview = copy.copy(self.image_decrypted)
        dec2_img = ImageTk.PhotoImage(self.image_decrypted_toview.resize(self.resize_image(self.image_decrypted_toview), Image.Resampling.LANCZOS))
        dec2_img_label = tk.Label(dec2_window, image=dec2_img)
        dec2_img_label.img = dec2_img  
        dec2_img_label.place(relx=0.29, rely=0.5, anchor='center')

        #button - zapisz obraz
        dec2_save_button = tk.Button(dec2_window, text = 'Zapisz obraz', width=15, height=1, bg=self.dark_gray_color, bd=0, command=lambda:self.save_img(dec2_window, self.image_decrypted, 2))
        dec2_save_button.place(relx=0.777, rely=0.219)

        #button - kopiuj obraz do schowka
        dec2_copy_button = tk.Button(dec2_window, text = 'Kopiuj obraz', width=15, height=1, bg=self.dark_gray_color, bd=0, command=lambda:self.copy_to_clipboard(self.image_decrypted))
        dec2_copy_button.place(relx=0.777, rely=0.35)
    
    def draw_histograms(self, im, fig_hist1, canvas_hist1, fig_hist2, canvas_hist2, fig_hist3, canvas_hist3): #rysowanie histogramów
        obj1 = fig_hist1.gca()
        obj2 = fig_hist2.gca()
        obj3 = fig_hist3.gca()
        
        obj1.hist([x[0] for x in list(im.getdata())], bins = 256, color = 'tab:red')
        obj1.set_title('R')
        canvas_hist1.draw()

        obj2.hist([x[1] for x in list(im.getdata())], bins = 256, color = 'tab:green')
        obj2.set_title('G')
        canvas_hist2.draw()

        obj3.hist([x[2] for x in list(im.getdata())], bins = 256, color = 'tab:blue')
        obj3.set_title('B')
        canvas_hist3.draw()

    def get_measures(self):
        #self.key_sensivity = self.controller.get_key_sensitivity(10**(-16))
        self.npcr = self.controller.get_npcr()
        self.uaci = self.controller.get_uaci()
        self.entropy = self.controller.get_entropy()
        self.correlations = self.controller.get_correlations()

    def key_sensitivity(self):
        im_oryg, im_x, im_p = self.controller.get_key_sensitivity(10**(-16))

        self.ax1.imshow(im_oryg)
        self.ax1.axes.get_xaxis().set_visible(False)
        self.ax1.axes.get_yaxis().set_visible(False)
        self.ax1.set_title('Obraz oryginalny')
        self.canvas_sens1.draw()

        self.ax2.imshow(im_x)
        self.ax2.axes.get_xaxis().set_visible(False)
        self.ax2.axes.get_yaxis().set_visible(False)
        self.ax2.set_title('Zmieniona wartość x')
        self.canvas_sens2.draw()

        self.ax3.imshow(im_p)
        self.ax3.axes.get_xaxis().set_visible(False)
        self.ax3.axes.get_yaxis().set_visible(False)
        self.ax3.set_title('Zmieniona wartość p')
        self.canvas_sens3.draw()
        
    def start_encryption(self):
        print(self.enc_x_entry.get(), self.enc_p_entry.get(), self.enc_option_radio.get())
        self.controller.set_x(float(self.enc_x_entry.get()))
        self.controller.set_p(float(self.enc_p_entry.get()))
        self.controller.set_ciphertype(float(self.enc_option_radio.get()))
        self.cryptogram = self.controller.start_encryption()
        self.spx = self.controller.get_Spx()
        print(np.asarray(self.cryptogram))
        self.enc_open_window()
        #self.routine(1)

    def start_decryption(self):
        self.controller.set_x(float(self.dec_x_entry.get()))
        self.controller.set_p(float(self.dec_p_entry.get()))
        self.controller.set_Spx(float(self.dec_key_entry.get()))
        self.controller.set_ciphertype(float(self.dec_option_radio.get()))
        self.image_decrypted = self.controller.start_decryption()
        #print(np.asarray(self.cryptogram))
        self.dec_open_window()
        #self.routine(1)
    
    def set_image_for_enc(self):
        print(self.image)
        self.image_toview = copy.copy(self.image)
        self.enc_image = self.image_toview.resize(self.resize_image(self.image_toview), Image.Resampling.LANCZOS)
        self.enc_image_tk = ImageTk.PhotoImage(self.enc_image)

        self.enc_image_label = ttk.Label(self.page_encode, image=self.enc_image_tk)
        self.enc_image_label.place(relx=0.71, rely=0.502, anchor='center')


    def set_image_for_dec(self):
        self.image_toview = copy.copy(self.image)
        self.dec_image = self.image_toview.resize(self.resize_image(self.image_toview), Image.Resampling.LANCZOS)
        self.dec_image_tk = ImageTk.PhotoImage(self.dec_image)

        self.dec_image_label = ttk.Label(self.page_decode, image=self.dec_image_tk)
        self.dec_image_label.place(relx=0.71, rely=0.502, anchor='center') 
    
