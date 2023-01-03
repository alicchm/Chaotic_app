from PIL import Image, ImageStat
import numpy as np
import collections as col
import random
from math import log2, sqrt

class Cipher:
    def __init__(self):
        #self.alg_num = 1 #default wybrany czyli np 1/2
        self.source_path = ''
        self.image = None
        self.x = None
        self.p = None
        self.Spx = None
        self.cipher_type = None
        self.destination_path = ''
        self.cryptogram = []
        self.decrypted_image = None


    def set_source_path(self, path):
        self.source_path = path
        print(self.source_path)
        self.set_image()

    def set_image(self):
        self.image = Image.open(self.source_path)

    def start_encryption(self):
        if self.source_path!='' and self.image!=None and self.x!=None and self.p!=None:
            if self.cipher_type == 1:
                self.cryptogram = self.encryption1(self.image, self.x, self.p)
                return self.cryptogram
            elif self.cipher_type == 2:
                self.cryptogram = self.encryption2(self.image, self.x, self.p)
                return self.cryptogram

    def start_decryption(self):
        if self.source_path!='' and self.image!=None and self.Spx!=None:
            if self.cipher_type == 1:
                self.decrypted_image = self.decryption1(self.image, self.Spx, self.x, self.p)
                return self.decrypted_image
            elif self.cipher_type == 2:
                self.decrypted_image = self.decryption2(self.image, self.Spx, self.x, self.p)
                return self.decrypted_image

    def get_ciphertype(self):
        return self.cipher_type

    def m_map(self, xk, p):
        if xk<=0.5 and xk>=0:
            #print((xk/p)*(2-(xk/p)))
            return ((xk/p)*(2-(xk/p)))
        elif xk<=1 and xk>0.5:
            #print(((1-xk)/p)*(2-((1-xk)/p)))
            return (((1-xk)/p)*(2-((1-xk)/p)))
    
    def asymetric_tent_map(self, xk, p):
        if xk<p and xk>0:
            return (xk/p)
        elif xk<1 and xk>=p:
            return ((1-xk)/(1-p))
        
    def to_hex(self, x):
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

    def to_decim(self, hexa):
        length = len(hexa) - 1
        dec = 0
        for digit in hexa:
            dec += digit*16**length
            length -= 1
        return dec

    def encryption2(self, im, x, p):
        ### CZYTANIE -> PERMUTACJA ###
        N,M = im.size
        print(im.size)
        im = np.asarray(im)
        #print(im)
        first_plc = []
        last_plc = []
        xk = x
        im_flatten = im.reshape(N*M,3)
        for i in range(len(im_flatten)):
            xk = self.m_map(xk,p)
            if xk <= 0.5:
                first_plc.append(im_flatten[i])
            elif xk > 0.5:
                last_plc.append(im_flatten[i])
                    
        last_plc_rev = last_plc[::-1]
        first_plc.extend(last_plc_rev)
        
        self.Spx = np.sum(im)
        Spx = self.Spx
        #first_plc = np.roll(first_plc, Spx) XDD
        
        px_list = []
        for i in range(M):
            px_list.append([])
            for j in range(N):
                px_list[i].append(first_plc[(i*N)+j])
        
        
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
                        xk_rounded = int(np.round(xk*(Spx/N*M), decimals = 3) * 100 )
                        taba.append(xk_rounded)
                        hexa[a] = (hexa[a] + xk_rounded) % 16
                    #print(hexa)
                    tmp_2.append(self.to_decim(hexa))
                    #print(tmp_2)
                tmp_1.append(tmp_2)       
            ciphered_im.append(tmp_1)
        cryptogram = Image.fromarray(np.uint8(ciphered_im))

        return cryptogram

    def decryption2(self, im, Spx, x1, p1):
        N,M = im.size
        #print(im.size)
        px = np.asarray(im)
        p = p1
        xk = x1
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
                        xk_rounded = int(np.round(xk*(Spx/N*M), decimals = 3) * 100 )
                        taba.append(xk_rounded)
                        hexa[a] = (hexa[a] - xk_rounded) % 16
                    #print(hexa)
                    tmp_2.append(self.to_decim(hexa))
                    #print(tmp_2)
                tmp_1.append(tmp_2)       
            decrypted_im.append(tmp_1)
        decrypted_im = np.asarray(decrypted_im)
        print(decrypted_im.size, N, M)
        #px = []
        xk = x1
        decrypted_im1 = decrypted_im.reshape(N*M,3)
        px_list = np.empty([len(decrypted_im1), 3])
        print(decrypted_im1)
        i = 0
        while len(decrypted_im1)>0:
            xk = self.m_map(xk,p)
            
            if xk <= 0.5: #pierwszy nieodczytany piksel
                px_list[i] = decrypted_im1[0]
                decrypted_im1 = np.delete(decrypted_im1, 0, 0)
                
            elif xk > 0.5: #ostatni nieodczytany piksel
                px_list[i] = decrypted_im1[len(decrypted_im1)-1]
                decrypted_im1 = np.delete(decrypted_im1, len(decrypted_im1)-1, 0)
            i=i+1  
        print(px_list)
        decode_px = []
        for i in range(M):
            decode_px.append([])
            for j in range(N):
                decode_px[i].append(px_list[(i*N)+j])
        decrypted_image =  Image.fromarray(np.uint8(decode_px))
        decrypted_image.save("odszyfrowane.jpg")
        return decrypted_image
        

    def generate_sbox(self, x, p, Spx, N, M):
        sn = list(np.arange(start=0,stop=256,step=1)) #lista [0,1,..,255]
        lengthSn = len(sn)
        sb = []
        #obliczenie wartości początkowej
        initial_val = (x+(Spx/(3*255*N*M)))%1
        
        #opuszczenie tysiąca pierwszych wartości x z rekurencji
        for i in range(10**3):
            initial_val = self.asymetric_tent_map(initial_val, p)
        
        xs = initial_val

        while lengthSn > 0:
            xs = self.asymetric_tent_map(xs, p) #calculate x from recurence
            index = (xs*lengthSn)//1 #calculate index
            index = int(index)
            sb.append(sn[index]) #add Sn[index] to Sb
            sn.pop(index) #remove from Sn element Sn[index]
            lengthSn -= 1 #decrease lengthSn by 1
            
        return sb

    def calc_spx(self, im):  # suma pikseli, klucz prywatny s-box
        px_sum = 0
        for i in range(0,len(im)):
            for j in range(0,len(im[i])):
                for k in range(0,len(im[i][j])):
                    px_sum += im[i][j][k]
        return px_sum

    def encryption1(self, im, x1, p1):
        I = np.asarray(im)
        N, M = im.size #szerokość, wysokość
        print('DZIAŁA')
        #obliczenie wartości klucza Spx
        self.Spx = self.calc_spx(I)
        Spx = self.Spx
        print(Spx)
        p = p1
        xk = x1
        sb = self.generate_sbox(xk, p, Spx, N, M)

        first_place = []
        last_place = []
        
        deque_sb = col.deque(sb) #zmiana typu "listy" żeby szybciej wykonywał się obrót cykliczny s-box
        print(xk, p)
        for i in range(M): #po wierszach obrazu
            for j in range(N): #po kolumnach obrazu
                xk = self.m_map(xk, p) #calculate xk from m_map
                #print(xk)
                #Read the S − box value for the pixels RGB components (S − box(px(i,j)));
                new_px_vals = [deque_sb[I[i][j][0]],deque_sb[I[i][j][1]],deque_sb[I[i][j][2]]] 

                if xk <= 0.5:
                    first_place.append(new_px_vals) #write value S − box(px(i,j)) in the first free place
                elif xk > 0.5:
                    last_place.append(new_px_vals) #write value S − box(px(i,j)) in the last free place
                
                shift = int((256*xk)//1) #calculate shift
                deque_sb.rotate(shift) #shift s-box
            #print(xk)
        #połączenie w całość pikseli zapisywanych od końca i od początku
        last_place_rv = last_place[::-1]
        first_place.extend(last_place_rv)
        #print(last_place_rv)
        #utworzenie nowej listy pikseli (zaszyfrowanych)
        px_list = []
        
        #zmiana budowy listy, by móc ją wczytać jako obraz rgb
        for i in range(M):
            px_list.append([])
            for j in range(N):
                px_list[i].append(first_place[(i*N)+j])
        #print(px_list)
        #zapisanie listy jako obraz
        cryptogram = Image.fromarray(np.uint8(px_list))
        print(np.asarray(cryptogram))

        return cryptogram

    def decryption1(self, cryptogram, Spx, x1, p1):
        J = np.asarray(cryptogram)
        enc_N, enc_M = cryptogram.size
        print('działa')
        J_flatter = J.reshape(enc_N*enc_M,3) #zmiana struktury na listę pikseli
        #J_flatter
        
        px_list2 = []
        xk2 = x1
        p = p1
        sb = self.generate_sbox(xk2, p, Spx, enc_N, enc_M)
        deque_sb = col.deque(sb) #zmiana typu "listy" żeby szybciej wykonywał się obrót cykliczny s-box
        print(J_flatter)
        while len(J_flatter)>0:
            xk2 = self.m_map(xk2, p) #calculate x from recurence

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
        print('działa')    
        #zmiana struktury listy, by móc ją potem odczytać jako obraz
        decode_px = []
        for i in range(enc_M):
            decode_px.append([])
            for j in range(enc_N):
                decode_px[i].append(px_list2[(i*enc_N)+j])

        decrypted = Image.fromarray(np.uint8(decode_px))
        return decrypted

    #MIARY (metoda draw histograms jest w w widoku)


    def key_sensitivity(self, change_value):
        
        if self.cipher_type==1:
            im_oryg = self.cryptogram
            im_x = self.encryption1(self.image, self.x+change_value, self.p)
            im_p = self.encryption1(self.image, self.x, self.p+change_value)
        else:
            im_oryg = self.cryptogram
            im_x = self.encryption2(self.image, self.x+change_value, self.p)
            im_p = self.encryption2(self.image, self.x, self.p+change_value)
        
        return im_oryg, im_x, im_p

    def npcr(self):
        N, M = self.image.size #szerokość, wysokość
        im2 = self.image.copy()
        im2_px = im2.load()
        random_N = random.randint(0, N-1)
        random_M = random.randint(0, M-1)
        im2_px[random_N, random_M] = ((im2_px[random_N, random_M][0]+1)%256, (im2_px[random_N, random_M][1]+1)%256, (im2_px[random_N, random_M][2]+1)%256)
        
        if self.cipher_type==1:
            enc_im = self.cryptogram
            enc_im2 = self.encryption1(im2, self.x, self.p)
        else:
            enc_im = self.cryptogram
            enc_im2 = self.encryption2(im2, self.x, self.p)
        
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

    #def npcr2(im1, im2):
    #    im1 = np.asarray(im1)
    #    im2 = np.asarray(im2)
    #    values = [0,0,0]
    #    for i in range(len(im1)):
    #        for j in range(len(im1[i])):
    #            for k in range(len(im1[i][j])):
    #                if im1[i][j][k] != im2[i][j][k]:
    #                    values[k]+=1
    #    length = im1.size/3
    #    values = [(x/length) * 100 for x in values]
    #    return values

    def uaci(self):
        N, M = self.image.size #szerokość, wysokość
        im2 = self.image.copy()
        im2_px = im2.load()
        random_N = random.randint(0, N-1)
        random_M = random.randint(0, M-1)
        im2_px[random_N, random_M] = ((im2_px[random_N, random_M][0]+1)%256, (im2_px[random_N, random_M][1]+1)%256, (im2_px[random_N, random_M][2]+1)%256)
        
        if self.cipher_type==1:
            enc_im = self.cryptogram
            enc_im2 = self.encryption1(im2, self.x, self.p)
        else:
            enc_im = self.cryptogram
            enc_im2 = self. encryption2(im2, self.x, self.p)
        
        enc_px = list(enc_im.getdata())
        enc_px2 = list(enc_im2.getdata())
        
        res = []
        
        for i in range(0,3): #dla każdego kanału RGB
            dif_sum = 0 
            for j in range(len(enc_px)): #obliczenie sumy ze wzoru
                dif_sum += (abs(enc_px[j][i] - enc_px2[j][i])/255)
            
            res.append(round((dif_sum/(N*M))*100,2))
        return res

    def entropy(self): #entropia
        r, g, b = self.cryptogram.split()
        
        results = []
        
        for i in (r,g,b):
            i = i.histogram()
            sum_channel = 0
            
            for j in i:
                sum_channel += - (j/sum(i))*(log2(j/sum(i)))
                
            results.append(round(sum_channel,4))
        return results

    def correlations(self, encrypted = 1):
        
        # if encrypted == 1:
        #     if self.cipher_type==1:
        #         im = self.encryption1(self.image, self.x, self.p)
        #     else:
        #         im = self.encryption2(self.image, self.x, self.p)

        # if self.cipher_type==1:
        #     im = self.encryption1(self.image, self.x, self.p)
        # else:
        #     im = self.encryption2(self.image, self.x, self.p)

        im = self.cryptogram
        
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