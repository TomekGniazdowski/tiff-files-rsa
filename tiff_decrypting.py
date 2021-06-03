import matplotlib.pyplot as plt
import numpy as np
import tiff_manipulations as tm
from tifffile.tifffile import imwrite

def return_sum_enc(vector):
    sum_of_elem = ''
    for i in range(0, len(vector)):
        sum_of_elem = sum_of_elem + vector[i]
    return sum_of_elem

def convert_list_hex_int(list):
    list_conv = []
    for e in list:
        list_conv.append(int(e, 16))
    return list_conv

def convert_list_int_hex(list):
    list_conv = []
    for e in list:
        list_conv.append(hex(e))
    return list_conv

class TiffDecrypting(tm.Tiff_manipulations):
    def __init__(self, file_name, len_of_c, n, d):
        super().__init__(file_name)
        self.read_data()
        self.list_data()
        # print('orginalny, cały:', self.data_hex_list)
        self.all_px = self.dic_values['length'] * self.dic_values['width']
        self.all_strips = ['0'] * self.all_px
        self.read_img()
        # print('orginalny, piksele:', self.all_strips)
        # print('orginalny, piksele, int:', self.convert_list_hex_int(self.all_strips))
        self.img = self.basic_img()
        # self.show_img(self.all_strips)
        # self.all_strips = self.convert_list_hex_int(self.all_strips)
        self.len_of_c = len_of_c
        self.n = n
        self.d = d
        print('n:', self.n, 'd:', self.d, 'dlugosc m:', self.len_of_c)

        self.divide_to_chunks(chunk_len=self.len_of_c)
        self.rsa_decrypt()
        self.connect_chunks_decrypted()
        img_out = np.array(self.data_hex_list_conn_2)
        img_out = convert_list_hex_int(img_out)
        img_out = np.array(img_out)
        # img_out = np.pad(img_out, (0, 1016 * 1016 - len(img_out)), 'constant')
        img_out = img_out.reshape(1016, 1016)
        img_out = img_out.astype(np.uint8)
        imwrite('obraz_ponownie_odkodowany.tif', img_out, photometric='minisblack')

    def show_img(self, strips):
        kdx = 0
        for i in range(1016):
            for j in range(1016):
                self.img[i][j] = int(strips[kdx], 16)
                kdx += 1
        plt.imshow(self.img, cmap='gray')
        plt.show()

    # return plain, black img
    def basic_img(self):
        img_pom = np.ones((self.dic_values['length'], self.dic_values['width']), np.uint8)
        return img_pom

    # reads all stripes, store them in 'self.all_strips'
    # 'kdx' - 'k' counter
    def read_img(self):
        # one strip
        if type(self.dic_values['strip_offsets']) == int:
            k = self.dic_values['strip_offsets']
            kdx = 0
            idx = 0
            while 1:
                self.all_strips[idx] = self.data_hex_list[k]
                k += 1
                kdx += 1
                idx += 1
                if kdx == self.all_px - 1:
                    break

        # many stripes
        if type(self.dic_values['strip_offsets']) == list:
            number_of_strips = len(self.dic_values['strip_offsets'])
            fulll_strip = self.dic_values['strip_byte_counts'][0]
            partial_strip = self.dic_values['strip_byte_counts'][number_of_strips - 1]
            kdx = 0
            strip_number = 0
            k = self.dic_values['strip_offsets'][strip_number]
            idx = 0
            while 1:
                self.all_strips[idx] = self.data_hex_list[k]
                k += 1
                kdx += 1
                idx += 1
                if kdx == fulll_strip and strip_number < number_of_strips - 1:
                    strip_number += 1
                    k = self.dic_values['strip_offsets'][strip_number]
                    kdx = 0
                if kdx == partial_strip and strip_number == number_of_strips - 1:
                    break

    # rsa decrypt
    def rsa_decrypt(self):
        self.data_hex_list_div_int_dec = [0] * (int((len(self.all_strips) / self.len_of_c)))
        idx = 0
        for chunk in self.data_hex_list_div_int_enc:
            self.data_hex_list_div_int_dec[idx] = pow(chunk, self.d, self.n)
            idx += 1
        # print('odkodowany:', self.data_hex_list_div_int_dec)

    # divides a stream of bytes into a list of substreams
    def divide_to_chunks(self, chunk_len):
        self.data_hex_list_div_int_enc = [self.all_strips[i:i + chunk_len] for i in
                                          range(0, len(self.all_strips), chunk_len)]
        for idx, chunk in enumerate(self.data_hex_list_div_int_enc):
            self.data_hex_list_div_int_enc[idx] = return_sum_enc(chunk)
        for idx, chunk in enumerate(self.data_hex_list_div_int_enc):
            self.data_hex_list_div_int_enc[idx] = int(chunk, 16)

    def connect_chunks_decrypted(self):
        self.data_hex_list_conn_1 = ['0' for x in range(len(self.data_hex_list_div_int_dec))]
        for idx, chunk in enumerate(self.data_hex_list_div_int_dec):
            self.data_hex_list_conn_1[idx] = hex(chunk).replace('0x', '')
        # print('odkodowany, hex:', self.data_hex_list_conn_1)

        self.data_hex_list_conn_2 = ['0' for x in range(len(self.data_hex_list_conn_1) * (self.len_of_c - 1))]
        kdx = 0
        for idx, chunk in enumerate(self.data_hex_list_conn_1):
            try:
                if len(chunk) < self.len_of_c * 2 - 2:
                    first_zeros = '0' * (self.len_of_c * 2 - 2 - len(chunk))
                    chunk = first_zeros + chunk
                for jdx in range(0, len(chunk), 2):
                    c = chunk[jdx:jdx + 2]
                    if len(c) == 2:
                        self.data_hex_list_conn_2[kdx] = c
                        kdx += 1
                    else:
                        self.data_hex_list_conn_2[kdx] = '0' + c
            except:
                break
        # print('odkodowany, podzielony na piksele, hex:', self.data_hex_list_conn_2)