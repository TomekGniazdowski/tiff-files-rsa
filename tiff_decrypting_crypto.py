import matplotlib.pyplot as plt
import numpy as np
import tiff_manipulations as tm
from tifffile.tifffile import imwrite
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa

def return_sum_enc(vector):
    sum_of_elem = b''
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

class TiffDecryptingcrypto(tm.Tiff_manipulations):
    def __init__(self, file_name, private_key):
        super().__init__(file_name)
        self.read_data()
        self.list_data()
        self.private_key = private_key
        # print('orginalny, cały:', self.data_hex_list)
        self.all_px = self.dic_values['length'] * self.dic_values['width']
        self.all_strips = ['0'] * self.all_px
        self.read_img()
        # print('orginalny, piksele:', self.all_strips)
        # print('orginalny, piksele, int:', self.convert_list_hex_int(self.all_strips))
        self.img = self.basic_img()
        # self.all_strips = self.convert_list_hex_int(self.all_strips)

        self.divide_to_chunks(chunk_len=128)
        self.rsa_decrypt()
        self.connect_chunks_decrypted()
        img_out = np.array(self.data_hex_list_conn_1)
        img_out = convert_list_hex_int(img_out)
        img_out = np.array(img_out)
        img_out = np.pad(img_out, (0, 1017 * 1016 - len(img_out)), 'constant')
        img_out = img_out.reshape(1017, 1016)
        img_out = img_out.astype(np.uint8)
        imwrite('obraz_ponownie_odkodowany_crypto.tif', img_out, photometric='minisblack')

    def show_img(self, strips):
        kdx = 0
        for i in range(1017):
            for j in range(1016):
                self.img[i][j] = strips[kdx]
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

    # rsa encyption using exp mod
    def rsa_decrypt(self):
        self.data_hex_list_div_dec = ['0'] * int(len(self.all_strips) / 128)
        for idx, chunk in enumerate(self.data_hex_list_div_int_enc):
            try:
                self.data_hex_list_div_dec[idx] = \
                    self.private_key.decrypt(chunk, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                                 algorithm=hashes.SHA256(), label=None))
            except:
                break

    # divides a stream of bytes into a list of substreams
    def divide_to_chunks(self, chunk_len):
        for idx, element in enumerate(self.all_strips):
            self.all_strips[idx] = bytes([int(element, 16)])

        self.data_hex_list_div_int_enc = [self.all_strips[i:i + chunk_len] for i in
                                          range(0, len(self.all_strips), chunk_len)]
        for idx, chunk in enumerate(self.data_hex_list_div_int_enc):
            self.data_hex_list_div_int_enc[idx] = return_sum_enc(chunk)

    def connect_chunks_decrypted(self):
        self.data_hex_list_conn_1 = ['0' for x in range(len(self.data_hex_list_div_dec) * 30)]
        print(len(self.data_hex_list_conn_1))
        kdx = 0
        for idx, chunk in enumerate(self.data_hex_list_div_dec):
            for jdx in range(0, len(chunk), 2):
                c = chunk[jdx:jdx + 2]
                if len(c) == 2:
                    self.data_hex_list_conn_1[kdx] = c
                    kdx += 1
