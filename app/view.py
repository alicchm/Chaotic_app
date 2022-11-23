import tkinter as tk
from tkinter import CENTER, LEFT, RIGHT, Toplevel, ttk, filedialog
from PIL import ImageTk, Image, ImageStat
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from io import BytesIO
import win32clipboard
from controller import Controller
import random
from math import log2, sqrt

#na czas implementacji
from tkinter.messagebox import showinfo

class View():
    def __init__(self, master):
        self.root = master
        self.controller = None
        #self.root = tk.Tk()
        self.root.geometry('566x345')
        self.root.title('Chaotyczny program')
        self.root.configure(bg="#242424")
        self.root.resizable(False, False) 

        self.root_icon = ImageTk.PhotoImage(file = 'app_logo_mini2.png')
        self.root.iconphoto(False, self.root_icon)

        #notebook = tworzenie zakładek
        self.enc_style_notebook = ttk.Style()
        self.enc_style_notebook.theme_use('clam')
        self.enc_style_notebook.configure('TNotebook.Tab', background='#dadad9')
        self.enc_style_notebook.configure('TNotebook', background='#242424', bordercolor='#242424')
        self.enc_style_notebook.map("TNotebook.Tab", background= [('selected', '#242424')], foreground=[('selected','#ffffff')])

        self.notebook = ttk.Notebook(self.root, style='TNotebook')
        self.notebook.grid(column=0, row=0)

        #tworzenie zakładek i dodanie ich do notebooka
        self.page_encode = tk.Frame(self.notebook, width=566, height=325, bg="#242424")
        self.page_decode = tk.Frame(self.notebook, width=566, height=325, bg="#242424")

        self.page_encode.grid(sticky='NESW')
        self.page_decode.grid(sticky='NESW')

        self.notebook.add(self.page_encode, text='Szyfrowanie')
        self.notebook.add(self.page_decode, text='Deszyfrowanie')

        #strona z kodowaniem
        #tło strony
        self.enc_bg_img = ImageTk.PhotoImage(Image.open("encode_bg5.jpg").resize((566,325), Image.Resampling.LANCZOS))
        self.enc_bgimg_label = tk.Label(self.page_encode, image=self.enc_bg_img, bg='#242424')
        self.enc_bgimg_label.img = self.enc_bg_img  
        self.enc_bgimg_label.place(relx=0.5, rely=0.5, anchor='center')

        #przycisk ładowania obrazu
        #page_encode.wm_attributes('-transparentcolor')
        self.enc_loadimg_button = tk.Button(self.page_encode, text = 'Ładuj obraz', command=self.enc_openimage, width=15, height=1, bg='#e59500', bd=0)
        self.enc_loadimg_button.place(relx=0.056, rely=0.1)

        #wybór algorytmu
        self.enc_option_radio = tk.IntVar()
        self.enc_style_radiobutton = ttk.Style()
        self.enc_style_radiobutton.configure('enc_radio.TRadiobutton', background='#e59500')

        self.enc_algorithm1_radio = ttk.Radiobutton(self.page_encode, text='Algorytm 1.', variable=self.enc_option_radio, value=1, command=self.enc_selectalgorithm, style='enc_radio.TRadiobutton')
        self.enc_algorithm1_radio.place(relx=0.07, rely=0.29)

        self.enc_algorithm2_radio = ttk.Radiobutton(self.page_encode, text='Algorytm 2.', variable=self.enc_option_radio, value=2, command=self.enc_selectalgorithm, style='enc_radio.TRadiobutton')
        self.enc_algorithm2_radio.place(relx=0.07, rely=0.38)

        #wartości x i p
        self.enc_x_label = tk.Label(self.page_encode, text='x:', bg='#e59500')
        self.enc_x_label.place(relx=0.07, rely=0.57)

        self.enc_x_spinbox = tk.Spinbox(self.page_encode, from_=0, to_=1, format='%10.4f', increment=0.001, validate='focusout', width=10, relief='flat', 
                            bd=0, buttondownrelief=tk.FLAT, buttonuprelief=tk.FLAT, bg='#FFC969')
        self.enc_x_spinbox.place(relx=0.105, rely=0.576)

        self.enc_p_label = tk.Label(self.page_encode, text='p:', bg='#e59500')
        self.enc_p_label.place(relx=0.07, rely=0.66)

        self.enc_p_spinbox = tk.Spinbox(self.page_encode, from_=0, to_=1, format='%10.4f', increment=0.001, validate='focusout', width=10, relief='flat', 
                            bd=0, buttondownrelief=tk.FLAT, buttonuprelief=tk.FLAT, bg='#FFC969')
        self.enc_p_spinbox.place(relx=0.105, rely=0.666)

        #szyfrowanie - start algorytmu
        self.enc_encode_button = tk.Button(self.page_encode, text = 'Szyfruj!', width=15, height=1, bg='#e59500', bd=0, command=self.enc_open_window)
        self.enc_encode_button.place(relx=0.056, rely=0.82)

        #wyświetlanie załadowanego obrazu
        self.enc_image = Image.open("lena.jpg")
        self.enc_image = self.enc_image.resize((270,270), Image.Resampling.LANCZOS)
        self.enc_image_tk = ImageTk.PhotoImage(self.enc_image)

        self.enc_image_label = ttk.Label(self.page_encode, image=self.enc_image_tk)
        self.enc_image_label.place(relx=0.425, rely=0.082)

        #strona z dekodowaniem
        #tło strony
        self.dec_bg_img = ImageTk.PhotoImage(Image.open("encode_bg5.jpg").resize((566,325), Image.Resampling.LANCZOS))
        self.dec_bgimg_label = tk.Label(self.page_decode, bg='#242424') #image=dec_bg_img,
        # dec_bgimg_label.img = enc_bg_img  
        # dec_bgimg_label.place(relx=0.5, rely=0.5, anchor='center')

        #przycisk ładowania obrazu
        #page_encode.wm_attributes('-transparentcolor')
        self.dec_loadimg_button = tk.Button(self.page_decode, text = 'Ładuj obraz', command=self.enc_openimage, width=15, height=1, bg='#e59500', bd=0)
        self.dec_loadimg_button.place(relx=0.056, rely=0.1)

        #wybór algorytmu
        self.dec_option_radio = tk.IntVar()
        self.dec_style_radiobutton = ttk.Style()
        self.dec_style_radiobutton.configure('dec_radio.TRadiobutton', background='#e59500')

        self.dec_algorithm1_radio = ttk.Radiobutton(self.page_decode, text='Algorytm 1.', variable=self.dec_option_radio, value=1, command=self.enc_selectalgorithm, style='dec_radio.TRadiobutton')
        self.dec_algorithm1_radio.place(relx=0.07, rely=0.29)

        self.dec_algorithm2_radio = ttk.Radiobutton(self.page_decode, text='Algorytm 2.', variable=self.dec_option_radio, value=2, command=self.enc_selectalgorithm, style='dec_radio.TRadiobutton')
        self.dec_algorithm2_radio.place(relx=0.07, rely=0.38)

        #wartości x i p
        self.dec_key_label = tk.Label(self.page_decode, text='klucz:', bg='#e59500')
        self.dec_key_label.place(relx=0.07, rely=0.57)

        self.dec_key_spinbox = tk.Spinbox(self.page_decode, from_=0, to_=100, format='%10.0f', increment=1, validate='focusout', width=10, relief='flat', 
                            bd=0, buttondownrelief=tk.FLAT, buttonuprelief=tk.FLAT, bg='#FFC969', justify=tk.RIGHT)
        self.dec_key_spinbox.place(relx=0.105, rely=0.676)

        #szyfrowanie - start algorytmu
        self.dec_encode_button = tk.Button(self.page_decode, text = 'Deszyfruj!', width=15, height=1, bg='#e59500', bd=0, command=self.dec_open_window)
        self.dec_encode_button.place(relx=0.056, rely=0.82)

        #wyświetlanie załadowanego obrazu
        self.dec_image = Image.open("encoded.png")
        self.dec_image = self.dec_image.resize((270,270), Image.Resampling.LANCZOS)
        self.dec_image_tk = ImageTk.PhotoImage(self.dec_image)

        self.dec_image_label = ttk.Label(self.page_decode, image=self.dec_image_tk)
        self.dec_image_label.place(relx=0.425, rely=0.082)

        #self.root.mainloop()

    def setController(self, controller):
        self.controller = controller


    def enc_openimage(self):
        enc_filename = filedialog.askopenfilename(
            title = 'Wybierz obraz',
            filetypes=[('Obraz JPG','*.jpg'),('Obraz PNG','*.png')]
        )

        showinfo(title='Wybrany plik', message=enc_filename)

    def enc_selectalgorithm(self):
        print('wybrano algorytm: ', self.enc_option_radio.get())

    def enc_open_window(self):
        enc2_window = Toplevel(self.root)
        enc2_window.geometry('566x345')
        enc2_window.title('Chaotyczny program - po szyfrowaniu')
        enc2_window.configure(bg='#242424')
        enc2_window.resizable(False, False)

        #strona z zakodowanym obrazem
        page2_encode_results = tk.Frame(enc2_window, width=566, height=325, bg="#242424")
        page2_encode_results.grid(column=0, row=0, sticky='news')

        #tło strony
        enc2_bg_img = ImageTk.PhotoImage(Image.open("encode2_bg2.jpg").resize((566,325), Image.Resampling.LANCZOS))
        enc2_bgimg_label = tk.Label(page2_encode_results, image=enc2_bg_img, bg='#242424')
        enc2_bgimg_label.img = enc2_bg_img  
        enc2_bgimg_label.place(relx=0.5, rely=0.5, anchor='center')
        
        #wyświetlenie zakodowanego obrazu
        enc2_img_base = Image.open("encoded.png")
        enc2_img = ImageTk.PhotoImage(enc2_img_base.resize((270,270), Image.Resampling.LANCZOS))
        enc2_img_label = tk.Label(page2_encode_results, image=enc2_img)
        enc2_img_label.img = enc2_img  
        enc2_img_label.place(relx=0.315, rely=0.5, anchor='center')

        #button - zapisz obraz
        enc2_save_button = tk.Button(page2_encode_results, text = 'Zapisz obraz', width=15, height=1, bg='#93A295', bd=0)
        enc2_save_button.place(relx=0.72, rely=0.14)

        #button - kopiuj obraz do schowka
        enc2_copy_button = tk.Button(page2_encode_results, text = 'Kopiuj obraz', width=15, height=1, bg='#93A295', bd=0, command=lambda:self.copy_to_clipboard(enc2_img_base))
        enc2_copy_button.place(relx=0.72, rely=0.31)

        #label - klucz
        enc2_key_label = tk.Label(page2_encode_results, text='Klucz:', bg='#93A295', width=15, justify=CENTER)
        enc2_key_label.place(relx=0.72, rely=0.49)

        #label - wartość klucza
        enc2_keyval_label = tk.Text(page2_encode_results, bg='#CED4CF', height=1, width=13, relief='flat', inactiveselectbackground='#CED4CF')
        enc2_keyval_label.insert(1.0,'1233456787')
        enc2_keyval_label.configure(state='disabled') #trzeba najpierw podać zawartość, potem zmienić stan
        enc2_keyval_label.place(relx=0.742, rely=0.578)

        #strona z miarami jakości
        page2_encode_measures = tk.Frame(enc2_window, width=566, height=325, bg="#242424")
        page2_encode_measures.grid(column=0, row=0, sticky='news')
        
        #tło strony
        enc2_meas_bg_img = ImageTk.PhotoImage(Image.open("encode2_measures_bg.jpg").resize((566,325), Image.Resampling.LANCZOS))
        enc2_meas_bgimg_label = tk.Label(page2_encode_measures, image=enc2_meas_bg_img, bg='#242424')
        enc2_meas_bgimg_label.img = enc2_meas_bg_img  
        enc2_meas_bgimg_label.place(relx=0.5, rely=0.5, anchor='center')

        #button - do wyników kodowania
        enc2_toresults_button = tk.Button(page2_encode_measures, text = 'Powrót', width=8, height=1, bg='#CED4CF', bd=0, command=lambda: self.change_frame(page2_encode_results))
        enc2_toresults_button.place(relx=0.04, rely=0.885)

        fig = plt.figure(figsize=(3,2),dpi=100)
        ax = fig.add_axes([0,0.1,0.8,0.8])
        line = FigureCanvasTkAgg(fig, page2_encode_measures)
        line.get_tk_widget().pack(side=tk.LEFT)
        line.draw()

        #button - do strony z miarami jakości
        enc2_tomeasures_button = tk.Button(page2_encode_results, text = 'Miary', width=8, height=1, bg='#CED4CF', bd=0, command=lambda: self.change_frame_calc(page2_encode_measures, line, ax))
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
        dec2_window.geometry('566x345')
        dec2_window.title('Chaotyczny program - po deszyfrowaniu')
        dec2_window.configure(bg='#242424')
        dec2_window.resizable(False, False)

        #wyświetlenie odkodowanego obrazu
        dec2_img_base = Image.open("lena.jpg")
        dec2_img = ImageTk.PhotoImage(dec2_img_base.resize((270,270), Image.Resampling.LANCZOS))
        dec2_img_label = tk.Label(dec2_window, image=dec2_img)
        dec2_img_label.img = dec2_img  
        dec2_img_label.place(relx=0.315, rely=0.5, anchor='center')

        #button - zapisz obraz
        dec2_save_button = tk.Button(dec2_window, text = 'Zapisz obraz', width=15, height=1, bg='#93A295', bd=0)
        dec2_save_button.place(relx=0.72, rely=0.14)

        #button - kopiuj obraz do schowka
        dec2_copy_button = tk.Button(dec2_window, text = 'Kopiuj obraz', width=15, height=1, bg='#93A295', bd=0, command=lambda:self.copy_to_clipboard(dec2_img_base))
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

    def key_sensitivity(im, x, p, change_value, alg_num):
        
        if alg_num==1:
            im_oryg = encryption1(im, x, p)
            im_x = encryption1(im, x+change_value, p)
            im_p = encryption1(im, x, p+change_value)
        else:
            im_oryg = encryption2(im, x, p)
            im_x = encryption2(im, x+change_value, p)
            im_p = encryption2(im, x, p+change_value)
        
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

    def npcr(im, x, p, alg_num):
        N, M = im.size #szerokość, wysokość
        im2 = im.copy()
        im2_px = im2.load()
        random_N = random.randint(0, N-1)
        random_M = random.randint(0, M-1)
        im2_px[random_N, random_M] = ((im2_px[random_N, random_M][0]+1)%256, (im2_px[random_N, random_M][1]+1)%256, (im2_px[random_N, random_M][2]+1)%256)
        
        if alg_num==1:
            enc_im = encryption1(im, x, p)
            enc_im2 = encryption1(im2, x, p)
        else:
            enc_im = encryption2(im, x, p)
            enc_im2 = encryption2(im2, x, p)
        
        enc_px = list(enc_im.getdata())
        enc_px2 = list(enc_im2.getdata())
        
        res = []
        
        for i in range(0,3): #dla każdego kanału RGB
            dif_sum = 0 
            for j in range(len(enc_px)): #obliczenie sumy ze wzoru
                if enc_px[j][i] != enc_px2[j][i]:
                    dif_sum += 1
            
            res.append(round((dif_sum/(N*M))*100,4))
            
        return res

    def npcr2(im1, im2):
        im1 = np.asarray(im1)
        im2 = np.asarray(im2)
        values = [0,0,0]
        for i in range(len(im1)):
            for j in range(len(im1[i])):
                for k in range(len(im1[i][j])):
                    if im1[i][j][k] != im2[i][j][k]:
                        values[k]+=1
        length = im1.size/3
        values = [(x/length) * 100 for x in values]
        return values

    def uaci(im, x, p, alg_num):
        N, M = im.size #szerokość, wysokość
        im2 = im.copy()
        im2_px = im2.load()
        random_N = random.randint(0, N-1)
        random_M = random.randint(0, M-1)
        im2_px[random_N, random_M] = ((im2_px[random_N, random_M][0]+1)%256, (im2_px[random_N, random_M][1]+1)%256, (im2_px[random_N, random_M][2]+1)%256)
        
        if alg_num==1:
            enc_im = encryption1(im, x, p)
            enc_im2 = encryption1(im2, x, p)
        else:
            enc_im = encryption2(im, x, p)
            enc_im2 = encryption2(im2, x, p)
        
        enc_px = list(enc_im.getdata())
        enc_px2 = list(enc_im2.getdata())
        
        res = []
        
        for i in range(0,3): #dla każdego kanału RGB
            dif_sum = 0 
            for j in range(len(enc_px)): #obliczenie sumy ze wzoru
                dif_sum += (abs(enc_px[j][i] - enc_px2[j][i])/255)
            
            res.append(round((dif_sum/(N*M))*100,2))
        return res

    def Entropy(image): #entropia
        r, g, b = image.split()
        
        results = []
        
        for i in (r,g,b):
            i = i.histogram()
            sum_channel = 0
            
            for j in i:
                sum_channel += - (j/sum(i))*(log2(j/sum(i)))
                
            results.append(round(sum_channel,4))
        return results

    def correlations(im, x, p, alg_num, encrypted = 1):
        
        if encrypted == 1:
            if alg_num==1:
                im = encryption1(im, x, p)
            else:
                im = encryption2(im, x, p)
        
        N, M = im.size
        r = []
            
        #horizontal
        im21 = im.crop((0,0,N-1,M))
        im22 = im.crop((1,0,N,M))
        
        stat21 = ImageStat.Stat(im21)
        stat22 = ImageStat.Stat(im22)
        stat21_mean = stat21.mean
        stat22_mean = stat22.mean
        
        im21_px = im21.load()
        im22_px = im22.load()
        
        r_temp = []
        for k in range(3):
            cov = 0
            var21 = 0
            var22 = 0
            for i in range(M):
                for j in range(N-1):
                    var21 += (im21_px[j,i][k] - stat21_mean[k])**2
                    var22 += (im22_px[j,i][k] - stat22_mean[k])**2
                    cov += (im21_px[j,i][k] - stat21_mean[k])*(im22_px[j,i][k] - stat22_mean[k])
                    
            cov = cov/N
            sigma21 = sqrt(var21/N)
            sigma22 = sqrt(var22/N)
            r_value = cov/(sigma21*sigma22)
            r_temp.append(round(r_value,4))
        r.append(r_temp)
        
        #vertical
        im31 = im.crop((0,0,N,M-1))
        im32 = im.crop((0,1,N,M))
        
        stat31 = ImageStat.Stat(im31)
        stat32 = ImageStat.Stat(im32)
        stat31_mean = stat31.mean
        stat32_mean = stat32.mean
        
        im31_px = im31.load()
        im32_px = im32.load()
        
        r_temp = []
        for k in range(3):
            cov = 0
            var31 = 0
            var32 = 0
            for i in range(M-1):
                for j in range(N):
                    var31 += (im31_px[j,i][k] - stat31_mean[k])**2
                    var32 += (im32_px[j,i][k] - stat32_mean[k])**2
                    cov += (im31_px[j,i][k] - stat31_mean[k])*(im32_px[j,i][k] - stat32_mean[k])
                    
            cov = cov/N
            sigma31 = sqrt(var31/N)
            sigma32 = sqrt(var32/N)
            r_value = cov/(sigma31*sigma32)
            r_temp.append(round(r_value,4))
        r.append(r_temp)
        
        #diagonal
        im41 = im.crop((0,0,N-1,M-1))
        im42 = im.crop((1,1,N,M))
        
        stat41 = ImageStat.Stat(im41)
        stat42 = ImageStat.Stat(im42)
        stat41_mean = stat41.mean
        stat42_mean = stat42.mean
        
        im41_px = im41.load()
        im42_px = im42.load()
        
        r_temp = []
        for k in range(3):
            cov = 0
            var41 = 0
            var42 = 0
            for i in range(M-1):
                for j in range(N-1):
                    var41 += (im41_px[j,i][k] - stat41_mean[k])**2
                    var42 += (im42_px[j,i][k] - stat42_mean[k])**2
                    cov += (im41_px[j,i][k] - stat41_mean[k])*(im42_px[j,i][k] - stat42_mean[k])
                    
            cov = cov/N
            sigma41 = sqrt(var41/N)
            sigma42 = sqrt(var42/N)
            r_value = cov/(sigma41*sigma42)
            r_temp.append(round(r_value,4))
        r.append(r_temp)
        
        return r