from PIL import Image, ImageStat
import numpy as np
import collections as col

class Cipher():
    def __init__(self):
        self.cipher_type = 'algorithm1' #default wybrany czyli np 1/2
        self.source_path = ''
        self.image = None
        self.x = None
        self.p = None
        self.Spx = None

        self.destination_path = ''
        self.cryptogram = None
        self.decrypted_image = None


    def set_source_path(self, path):
        self.source_path = path
        self.set_image()

    def set_image(self):
        self.image = Image.open(self.path)


    def start_encryption(self):
        if self.cipher_type == 'algorytm1':
            self.encryption1(self)
        elif self.cipher_type == 'algorytm2':
            self.encryption2(self)

    def get_ciphertyper(self, value):
        return self.cipher_type

    def m_map (xk, p):
        if xk<=0.5 and xk>=0:
            return ((xk/p)*(2-(xk/p)))
        elif xk<=1 and xk>0.5:
            return (((1-xk)/p)*(2-((1-xk)/p)))
    
    def asymetric_tent_map(xk,p):
        if xk<p and xk>0:
            return (xk/p)
        elif xk<1 and xk>=p:
            return ((1-xk)/(1-p))
        
    def to_hex(x):
        if x == 0:
            return [0, 0]
        hexa= []
        while x>0:
            check = x%16
            hexa.insert(0,check)
            x = x // 16
        if len(hexa)==0:
            hexa.append(0)
        elif len(hexa)==1:
            hexa.insert(0, 0)
        return hexa
    #print(to_hex(255))

    def to_decim(hexa):
        length = len(hexa) - 1
        dec = 0
        for digit in hexa:
            dec += digit*16**length
            length -= 1
        return dec

    def encryption2(self):
        ### CZYTANIE -> PERMUTACJA ###
        N,M = im.size
        print(im.size)
        im = np.asarray(self.image)
        x = self.x
        p = self.p
        #print(im)
        first_plc = []
        last_plc = []
        xk = x
        for i in range(len(im)):
            for j in range(len(im[i])):
                xk = self.m_map(xk,p)
                if xk <= 0.5:
                    first_plc.append(im[i,j])
                elif xk > 0.5:
                    last_plc.append(im[i,j])
                    
        last_plc_rev = last_plc[::-1]
        first_plc.extend(last_plc_rev)
        
        self.Spx = np.sum(im)
        Spx = self.Spx
        #first_plc = np.roll(first_plc, Spx) XDD
        
        px_list = []
        for i in range(M):
            px_list.append([])
            for j in range(N):
                px_list[i].append(first_plc[(i*M)+j])
        
        
        px = np.asarray(px_list)
        ### ZAPISYWANIE -> system szesnastkowy + dodawanie modulo ###
        ciphered_im = []
        xk = x
        print(len(px))
        print(xk)
        taba = []
        for i in range(len(px)):
            tmp_1 = []
            for j in range(len(px[i])):
                tmp_2 = []
                for k in range(len(px[i][j])):
                    hexa = self.to_hex(px[i][j][k])
                    #print(hexa)
                    for a in range(len(hexa)):
                        xk = self.asymetric_tent_map(xk,p)
                        #print(xk)
                        xk_rounded = int(round(xk,3) * 100)
                        taba.append(xk_rounded)
                        hexa[a] = (hexa[a] + xk_rounded * Spx) % 16
                    #print(hexa)
                    tmp_2.append(self.to_decim(hexa))
                    #print(tmp_2)
                tmp_1.append(tmp_2)       
            ciphered_im.append(tmp_1)
        self.cryptogram = Image.fromarray(np.uint8(ciphered_im))

    def decryption2(self):
        N,M = self.Image.size
        #print(im.size)
        px = np.asarray(self.image)
        x = self.x
        p = self.p
        Spx = self.Spx
        xk = x
        decrypted_im = []
        taba = []
        for i in range(len(px)):
            tmp_1 = []
            for j in range(len(px[i])):
                tmp_2 = []
                for k in range(len(px[i][j])):
                    hexa = self.to_hex(px[i][j][k])
                    #print(hexa)
                    for a in range(len(hexa)):
                        xk = self.asymetric_tent_map(xk,p)
                        #print(xk)
                        xk_rounded = int(round(xk,3) * 100 )
                        taba.append(xk_rounded)
                        hexa[a] = (hexa[a] - xk_rounded * Spx) % 16
                    #print(hexa)
                    tmp_2.append(self.to_decim(hexa))
                    #print(tmp_2)
                tmp_1.append(tmp_2)       
            decrypted_im.append(tmp_1)
        decrypted_im = np.asarray(decrypted_im)
        print(decrypted_im.size)
        #px = []
        xk = x
        decrypted_im = decrypted_im.reshape(N*M,3)
        px_list = np.empty([len(decrypted_im), 3])
        i = 0
        while len(decrypted_im)>0:
            xk = self.m_map(xk,p)
            
            if xk <= 0.5: #pierwszy nieodczytany piksel
                px = decrypted_im[0]
                decrypted_im = np.delete(decrypted_im, 0, 0)
                px_list[i] = px
                
            elif xk > 0.5: #ostatni nieodczytany piksel
                px = decrypted_im[len(decrypted_im)-1]
                decrypted_im = np.delete(decrypted_im, len(decrypted_im)-1, 0)
                px_list[i] = px
            i=i+1  
        print(px_list)
        #px_list = np.roll(px_list, -Spx) XDxdDd
        decode_px = []
        for i in range(M):
            decode_px.append([])
            for j in range(N):
                decode_px[i].append(px_list[(i*M)+j])
        self.decrypted_image =  Image.fromarray(np.uint8(decode_px))
        
        return decode_px
        

    def generate_sbox(self, Spx, N, M):
        sn = list(np.arange(start=0,stop=256,step=1)) #lista [0,1,..,255]
        lengthSn = len(sn)
        sb = []

        #obliczenie wartości początkowej
        initial_val = (self.x+(Spx/(3*255*N*M)))%1
        
        #opuszczenie tysiąca pierwszych wartości x z rekurencji
        for i in range(10**3):
            initial_val = self.asymetric_tent_map(initial_val, self.p)
        
        xs = initial_val

        while lengthSn > 0:
            xs = self.asymetric_tent_map(xs,self.p) #calculate x from recurence
            index = (xs*lengthSn)//1 #calculate index
            index = int(index)
            sb.append(sn[index]) #add Sn[index] to Sb
            sn.pop(index) #remove from Sn element Sn[index]
            lengthSn -= 1 #decrease lengthSn by 1
            
        return sb

    def encryption1(self):
        I = np.asarray(self.im)
        N, M = self.im.size #szerokość, wysokość
        
        #obliczenie wartości klucza Spx
        Spx = self.calc_spx(I)
        print(Spx)
            
        sb = self.generate_sbox(Spx, N, M)
        
        xk = self.x
        first_place = []
        last_place = []

        deque_sb = self.col.deque(sb) #zmiana typu "listy" żeby szybciej wykonywał się obrót cykliczny s-box

        for i in range(M): #po wierszach obrazu
            for j in range(N): #po kolumnach obrazu
                xk = self.m_map(xk, self.p) #calculate xk from m_map

                #Read the S − box value for the pixels RGB components (S − box(px(i,j)));
                new_px_vals = [deque_sb[I[i][j][0]],deque_sb[I[i][j][1]],deque_sb[I[i][j][2]]] 

                if xk <= 0.5:
                    first_place.append(new_px_vals) #write value S − box(px(i,j)) in the first free place
                elif xk > 0.5:
                    last_place.append(new_px_vals) #write value S − box(px(i,j)) in the last free place

                shift = int((256*xk)//1) #calculate shift
                deque_sb.rotate(shift) #shift s-box
                
        #połączenie w całość pikseli zapisywanych od końca i od początku
        last_place_rv = last_place[::-1]
        first_place.extend(last_place_rv)
        
        #utworzenie nowej listy pikseli (zaszyfrowanych)
        px_list = []
        
        #zmiana budowy listy, by móc ją wczytać jako obraz rgb
        for i in range(M):
            px_list.append([])
            for j in range(N):
                px_list[i].append(first_place[(i*M)+j])
        
        #zapisanie listy jako obraz
        self.cryptogram = Image.fromarray(np.uint8(px_list))
        
        return self.cryptogram

    def decryption1(self):
        J = np.asarray(self.cryptogram)
        enc_N, enc_M = self.cryptogram.size
        
        J_flatter = J.reshape(enc_N*enc_M,3) #zmiana struktury na listę pikseli
        J_flatter
        
        sb = self.generate_sbox(self.Spx, enc_N, enc_M)
        
        px_list2 = []
        xk2 = self.x
        
        deque_sb = col.deque(sb) #zmiana typu "listy" żeby szybciej wykonywał się obrót cykliczny s-box

        while len(J_flatter)>0:
            xk2 = self.m_map(xk2, self.p) #calculate x from recurence

            if xk2 <= 0.5: #pierwszy nieodczytany piksel
                px = J_flatter[0]
                J_flatter = np.delete(J_flatter, 0, 0)
            elif xk2 > 0.5: #ostatni nieodczytany piksel
                px = J_flatter[len(J_flatter)-1]
                J_flatter = np.delete(J_flatter, len(J_flatter)-1, 0)

            pixels = []

            for i in px: #dla każdej z wartości rgb danego piksela
                px_index = deque_sb.index(int(i)) #znalezienie pod którym indeksem leży dana wartość rgb
                pixels.append(px_index)
            px_list2.append(pixels) #dodanie nowych (odszyfrowanych) wartości pikseli do listy

            shift = int((256*xk2)//1) #obliczenie wartości shift
            deque_sb.rotate(shift) #shift s-box
            
        #zmiana struktury listy, by móc ją potem odczytać jako obraz
        decode_px = []
        for i in range(enc_M):
            decode_px.append([])
            for j in range(enc_N):
                decode_px[i].append(px_list2[(i*enc_M)+j])
                
        self.cryptogram = Image.fromarray(np.uint8(decode_px))


    #MIARY (metoda draw histograms jest w w widoku)
        