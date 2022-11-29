import tkinter as tk
from tkinter import CENTER, LEFT, RIGHT, Toplevel, ttk, filedialog
from PIL import ImageTk, Image, ImageStat
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from io import BytesIO
import win32clipboard
from controller import Controller

#na czas implementacji
from tkinter.messagebox import showinfo

class View():
    def __init__(self, master):
        self.root = master
        self.root.protocol("WM_DELETE_WINDOW", self.app_close)
        self.controller = None

        #miary
        self.key_sensivity = None
        self.npcr = None
        self.uaci = None
        self.entropy = None
        self.get_correlations = None

        #rozmiary okien, obrazów itp.
        self.root_window_width = 570
        self.root_window_height = 355
        self.small_window_width = 566
        self.small_window_height = 345
        self.nb_page_width = 566
        self.nb_page_height = 325
        self.max_image_width = 270
        self.max_image_height = 270

        #paleta kolorów
        self.dark_bg_color = "#242424"
        self.offwhite_color = "#f5f5f5"
        self.white_color = "#ffffff"
        self.orange_color = "#e59500"
        self.light_orange_color = "#FFC969"
        self.dark_gray_color = "#93A295"
        self.light_gray_color = "#CED4CF"

        self.root.geometry(f'{self.root_window_width}x{self.root_window_height}')
        self.root.title('Chaotyczny program')
        self.root.configure(bg=self.dark_bg_color)
        self.root.resizable(False, False) 

        self.root_icon = ImageTk.PhotoImage(file = 'app_logo_mini2.png')
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

        self.notebook.add(self.page_encode, text='Szyfrowanie')
        self.notebook.add(self.page_decode, text='Deszyfrowanie')
        self.notebook.add(self.page_description, text='Opis algorytmów')

        #strona z kodowaniem
        #tło strony
        self.enc_bg_img = ImageTk.PhotoImage(Image.open("encode_bg5.jpg").resize((self.nb_page_width,self.nb_page_height), Image.Resampling.LANCZOS))
        self.enc_bgimg_label = tk.Label(self.page_encode, image=self.enc_bg_img, bg=self.dark_bg_color)
        self.enc_bgimg_label.img = self.enc_bg_img  
        self.enc_bgimg_label.place(relx=0.5, rely=0.5, anchor='center')

        #przycisk ładowania obrazu
        #page_encode.wm_attributes('-transparentcolor')
        self.enc_loadimg_button = tk.Button(self.page_encode, text = 'Ładuj obraz', command=self.enc_openimage, width=15, height=1, bg=self.orange_color, bd=0)
        self.enc_loadimg_button.place(relx=0.056, rely=0.1)

        #wybór algorytmu
        self.enc_option_radio = tk.IntVar()
        self.enc_style_radiobutton = ttk.Style()
        self.enc_style_radiobutton.configure('enc_radio.TRadiobutton', background=self.orange_color)

        self.enc_algorithm1_radio = ttk.Radiobutton(self.page_encode, text='Algorytm 1.', variable=self.enc_option_radio, value=1, command=self.enc_selectalgorithm, style='enc_radio.TRadiobutton')
        self.enc_algorithm1_radio.place(relx=0.07, rely=0.29)

        self.enc_algorithm2_radio = ttk.Radiobutton(self.page_encode, text='Algorytm 2.', variable=self.enc_option_radio, value=2, command=self.enc_selectalgorithm, style='enc_radio.TRadiobutton')
        self.enc_algorithm2_radio.place(relx=0.07, rely=0.38)

        #wartości x i p
        self.enc_x_label = tk.Label(self.page_encode, text='x:', bg=self.orange_color)
        self.enc_x_label.place(relx=0.07, rely=0.57)

        self.enc_x_spinbox = tk.Spinbox(self.page_encode, from_=0, to_=1, format='%10.4f', increment=0.001, validate='focusout', width=10, relief='flat', 
                            bd=0, buttondownrelief=tk.FLAT, buttonuprelief=tk.FLAT, bg=self.light_orange_color)
        self.enc_x_spinbox.place(relx=0.105, rely=0.576)

        self.enc_p_label = tk.Label(self.page_encode, text='p:', bg=self.orange_color)
        self.enc_p_label.place(relx=0.07, rely=0.66)

        self.enc_p_spinbox = tk.Spinbox(self.page_encode, from_=0, to_=1, format='%10.4f', increment=0.001, validate='focusout', width=10, relief='flat', 
                            bd=0, buttondownrelief=tk.FLAT, buttonuprelief=tk.FLAT, bg=self.light_orange_color)
        self.enc_p_spinbox.place(relx=0.105, rely=0.666)

        #szyfrowanie - start algorytmu
        self.enc_encode_button = tk.Button(self.page_encode, text = 'Szyfruj!', width=15, height=1, bg=self.orange_color, bd=0, command=self.enc_open_window)
        self.enc_encode_button.place(relx=0.056, rely=0.82)

        #wyświetlanie załadowanego obrazu
        self.enc_image = Image.open("lena.jpg")

        self.enc_image = self.enc_image.resize(self.resize_image(self.enc_image), Image.Resampling.LANCZOS)
        self.enc_image_tk = ImageTk.PhotoImage(self.enc_image)

        self.enc_image_label = ttk.Label(self.page_encode, image=self.enc_image_tk)
        self.enc_image_label.place(relx=0.425, rely=0.082)

        #strona z dekodowaniem
        #tło strony
        self.dec_bg_img = ImageTk.PhotoImage(Image.open("encode_bg5.jpg").resize((self.nb_page_width,self.nb_page_height), Image.Resampling.LANCZOS))
        self.dec_bgimg_label = tk.Label(self.page_decode, bg=self.dark_bg_color) #image=dec_bg_img,
        # dec_bgimg_label.img = enc_bg_img  
        # dec_bgimg_label.place(relx=0.5, rely=0.5, anchor='center')

        #przycisk ładowania obrazu
        #page_encode.wm_attributes('-transparentcolor')
        self.dec_loadimg_button = tk.Button(self.page_decode, text = 'Ładuj obraz', command=self.enc_openimage, width=15, height=1, bg=self.orange_color, bd=0)
        self.dec_loadimg_button.place(relx=0.056, rely=0.1)

        #wybór algorytmu
        self.dec_option_radio = tk.IntVar()
        self.dec_style_radiobutton = ttk.Style()
        self.dec_style_radiobutton.configure('dec_radio.TRadiobutton', background=self.orange_color)

        self.dec_algorithm1_radio = ttk.Radiobutton(self.page_decode, text='Algorytm 1.', variable=self.dec_option_radio, value=1, command=self.enc_selectalgorithm, style='dec_radio.TRadiobutton')
        self.dec_algorithm1_radio.place(relx=0.07, rely=0.29)

        self.dec_algorithm2_radio = ttk.Radiobutton(self.page_decode, text='Algorytm 2.', variable=self.dec_option_radio, value=2, command=self.enc_selectalgorithm, style='dec_radio.TRadiobutton')
        self.dec_algorithm2_radio.place(relx=0.07, rely=0.38)

        #wartości x i p
        self.dec_key_label = tk.Label(self.page_decode, text='klucz:', bg=self.orange_color)
        self.dec_key_label.place(relx=0.07, rely=0.57)

        self.dec_key_spinbox = tk.Spinbox(self.page_decode, from_=0, to_=100, format='%10.0f', increment=1, validate='focusout', width=10, relief='flat', 
                            bd=0, buttondownrelief=tk.FLAT, buttonuprelief=tk.FLAT, bg=self.light_orange_color, justify=tk.RIGHT)
        self.dec_key_spinbox.place(relx=0.105, rely=0.676)

        #szyfrowanie - start algorytmu
        self.dec_encode_button = tk.Button(self.page_decode, text = 'Deszyfruj!', width=15, height=1, bg=self.orange_color, bd=0, command=self.dec_open_window)
        self.dec_encode_button.place(relx=0.056, rely=0.82)

        #wyświetlanie załadowanego obrazu
        self.dec_image = Image.open("encoded.png")
        self.dec_image = self.dec_image.resize(self.resize_image(self.dec_image), Image.Resampling.LANCZOS)
        self.dec_image_tk = ImageTk.PhotoImage(self.dec_image)

        self.dec_image_label = ttk.Label(self.page_decode, image=self.dec_image_tk)
        self.dec_image_label.place(relx=0.425, rely=0.082)

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

    def setController(self, controller):
        self.controller = controller

    def enc_openimage(self):
        enc_filename = filedialog.askopenfilename(
            title = 'Wybierz obraz',
            filetypes=[('Obraz JPG','*.jpg')]
        )

        showinfo(title='Wybrany plik', message=enc_filename)

    def resize_image(self, img):
        width, height = img.size
        if width>height:
            if width>self.max_image_width:
                height = (height*self.max_image_width)/width
                width = self.max_image_width
        else:
            width = (width*self.max_image_height)/height
            height = self.max_image_height
        
        return int(width), int(height)

    def enc_selectalgorithm(self):
        print('wybrano algorytm: ', self.enc_option_radio.get())

    def app_close(self):
        self.root.quit()
        self.root.destroy()

    def inner_window_close(self, win):
        # win.quit()
        win.destroy()

    def enc_open_window(self):
        enc2_window = Toplevel(self.root)
        enc2_window.geometry(f'{self.small_window_width}x{self.small_window_height}')
        enc2_window.title('Chaotyczny program - po szyfrowaniu')
        enc2_window.configure(bg=self.dark_bg_color)
        enc2_window.resizable(False, False)
        enc2_window.protocol("WM_DELETE_WINDOW", lambda: self.inner_window_close(enc2_window))

        #strona z zakodowanym obrazem
        page2_encode_results = tk.Frame(enc2_window, width=self.nb_page_width, height=self.nb_page_height, bg=self.dark_bg_color)
        page2_encode_results.grid(column=0, row=0, sticky='news')

        #tło strony
        enc2_bg_img = ImageTk.PhotoImage(Image.open("encode2_bg2.jpg").resize((self.nb_page_width,self.nb_page_height), Image.Resampling.LANCZOS))
        enc2_bgimg_label = tk.Label(page2_encode_results, image=enc2_bg_img, bg=self.dark_bg_color)
        enc2_bgimg_label.img = enc2_bg_img  
        enc2_bgimg_label.place(relx=0.5, rely=0.5, anchor='center')
        
        #wyświetlenie zakodowanego obrazu
        enc2_img_base = Image.open("encoded.png")
        enc2_img = ImageTk.PhotoImage(enc2_img_base.resize(self.resize_image(enc2_img_base), Image.Resampling.LANCZOS))
        enc2_img_label = tk.Label(page2_encode_results, image=enc2_img)
        enc2_img_label.img = enc2_img  
        enc2_img_label.place(relx=0.315, rely=0.5, anchor='center')

        #button - zapisz obraz
        enc2_save_button = tk.Button(page2_encode_results, text = 'Zapisz obraz', width=15, height=1, bg=self.dark_gray_color, bd=0)
        enc2_save_button.place(relx=0.72, rely=0.14)

        #button - kopiuj obraz do schowka
        enc2_copy_button = tk.Button(page2_encode_results, text = 'Kopiuj obraz', width=15, height=1, bg=self.dark_gray_color, bd=0, command=lambda:self.copy_to_clipboard(enc2_img_base))
        enc2_copy_button.place(relx=0.72, rely=0.31)

        #label - klucz
        enc2_key_label = tk.Label(page2_encode_results, text='Klucz:', bg=self.dark_gray_color, width=15, justify=CENTER)
        enc2_key_label.place(relx=0.72, rely=0.49)

        #label - wartość klucza
        enc2_keyval_label = tk.Text(page2_encode_results, bg=self.light_gray_color, height=1, width=13, relief='flat', inactiveselectbackground=self.light_gray_color)
        enc2_keyval_label.insert(1.0,'1233456787')
        enc2_keyval_label.configure(state='disabled') #trzeba najpierw podać zawartość, potem zmienić stan
        enc2_keyval_label.place(relx=0.742, rely=0.578)

        #strona z miarami jakości
        page2_encode_measures = tk.Frame(enc2_window, width=self.nb_page_width, height=self.nb_page_height, bg=self.dark_bg_color)
        page2_encode_measures.grid(column=0, row=0, sticky='news')
        
        #tło strony
        enc2_meas_bg_img = ImageTk.PhotoImage(Image.open("encode2_measures_bg.jpg").resize((self.nb_page_width,self.nb_page_height), Image.Resampling.LANCZOS))
        enc2_meas_bgimg_label = tk.Label(page2_encode_measures, image=enc2_meas_bg_img, bg=self.dark_bg_color)
        enc2_meas_bgimg_label.img = enc2_meas_bg_img  
        enc2_meas_bgimg_label.place(relx=0.5, rely=0.5, anchor='center')

        #button - do wyników kodowania
        enc2_toresults_button = tk.Button(page2_encode_measures, text = 'Powrót', width=8, height=1, bg=self.light_gray_color, bd=0, command=lambda: self.change_frame(page2_encode_results))
        enc2_toresults_button.place(relx=0.04, rely=0.885)

        fig = plt.figure(figsize=(3,2),dpi=100)
        ax = fig.add_axes([0,0.1,0.8,0.8])
        line = FigureCanvasTkAgg(fig, page2_encode_measures)
        line.get_tk_widget().pack(side=tk.LEFT)
        line.draw()

        #button - do strony z miarami jakości
        enc2_tomeasures_button = tk.Button(page2_encode_results, text = 'Miary', width=8, height=1, bg=self.light_gray_color, bd=0, command=lambda: self.change_frame_calc(page2_encode_measures, line, ax))
        enc2_tomeasures_button.place(relx=0.86, rely=0.885)

        self.change_frame(page2_encode_results) #żeby na starcie była otwarta pierwsza strona

    def change_frame(self, frame):
        frame.tkraise()

    def change_frame_calc(self, frame, line, ax):
        self.change_frame(frame)

        #obliczenie miar itp

        #przykładowy wykres
        ax.clear()
        t = np.arange(0.0, 2.0, 0.01)
        s = 1 + np.sin(2 * np.pi * t)
        # fig = plt.Figure(figsize=(3,2), dpi=100)
        # ax = fig.add_subplot(111)
        ax.plot(t,s)
        line.draw()
        # line.get_tk_widget().pack(side=tk.LEFT) #, fill=tk.BOTH
        # return fig

    def copy_to_clipboard(self, image1): #kopiowanie obrazu do schowka
        output = BytesIO()
        image1.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

    def dec_open_window(self):
        dec2_window = Toplevel(self.root)
        dec2_window.geometry(f'{self.small_window_width}x{self.small_window_height}')
        dec2_window.title('Chaotyczny program - po deszyfrowaniu')
        dec2_window.configure(bg=self.dark_bg_color)
        dec2_window.resizable(False, False)
        dec2_window.protocol("WM_DELETE_WINDOW", lambda: self.inner_window_close(dec2_window))

        #wyświetlenie odkodowanego obrazu
        dec2_img_base = Image.open("lena.jpg")
        dec2_img = ImageTk.PhotoImage(dec2_img_base.resize(self.resize_image(dec2_img_base), Image.Resampling.LANCZOS))
        dec2_img_label = tk.Label(dec2_window, image=dec2_img)
        dec2_img_label.img = dec2_img  
        dec2_img_label.place(relx=0.315, rely=0.5, anchor='center')

        #button - zapisz obraz
        dec2_save_button = tk.Button(dec2_window, text = 'Zapisz obraz', width=15, height=1, bg=self.dark_gray_color, bd=0)
        dec2_save_button.place(relx=0.72, rely=0.14)

        #button - kopiuj obraz do schowka
        dec2_copy_button = tk.Button(dec2_window, text = 'Kopiuj obraz', width=15, height=1, bg=self.dark_gray_color, bd=0, command=lambda:self.copy_to_clipboard(dec2_img_base))
        dec2_copy_button.place(relx=0.72, rely=0.31)
    
    def draw_histograms(im): #rysowanie histogramów

        plt.hist([x[0] for x in list(im.getdata())], bins = 256, color = 'tab:red')
        plt.ylim((0,4000))
        plt.show()
        plt.hist([x[1] for x in list(im.getdata())], bins = 256, color = 'tab:green')
        plt.ylim((0,4000))
        plt.show()
        plt.hist([x[2] for x in list(im.getdata())], bins = 256, color = 'tab:blue')
        plt.ylim((0,4000))
        plt.show()

    def get_measures(self):
        self.key_sensivity = self.controller.get_key_sensivity()
        self.npcr = self.controller.get_npcr()
        self.uaci = self.controller.get_uaci()
        self.entropy = self.controller.get_entropy()
        self.get_correlations = self.controller.get_correlations()

    def key_sensivity(self):
        im_oryg, im_x, im_p = self.key_sensivity()
        plt.figure(figsize=(20,10))
        
        plt.subplot(1,3,1)
        plt.axis('off')
        plt.imshow(im_oryg)
        
        plt.subplot(1,3,2)
        plt.axis('off')
        plt.imshow(im_x)
        
        plt.subplot(1,3,3)
        plt.axis('off')
        plt.imshow(im_p)
    

    