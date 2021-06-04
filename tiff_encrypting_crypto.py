from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
import matplotlib.pyplot as plt
import numpy as np
from tifffile.tifffile import imwrite
import tiff_manipulations as tm


def return_sum_enc(vector):
    sum_of_elem = ''
    for i in range(0, len(vector)):
        sum_of_elem = sum_of_elem + vector[i]
    sum_of_elem = bytes(sum_of_elem, 'utf-8')
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


class TiffEncryptingcrypto(tm.Tiff_manipulations):
    def __init__(self, file_name, n, e, d, p, q, len_of_m):
        super().__init__(file_name)
        self.read_data()
        # self.list_data()
        # print('orginalny, cały:', self.data_hex_list)
        self.all_px = self.dic_values['length'] * self.dic_values['width']
        self.all_strips = ['0'] * self.all_px
        self.read_img()
        # print('orginalny, piksele:', self.all_strips)
        # print('orginalny, piksele, int:', self.convert_list_hex_int(self.all_strips))
        self.img = self.basic_img()
        self.show_img(self.all_strips)

        # RSA
        self.p = p
        self.q = q
        self.e = e
        self.n = n
        self.d = d
        self.len_of_m = 30
        self.generate_keys()
        print('e:', self.e, 'n:', self.n, 'd:', self.d, 'dlugosc m:', self.len_of_m)
        # dividing
        self.divide_to_chunks(chunk_len=self.len_of_m)
        # RSA
        self.rsa_encrypt()
        self.connect_chunks_encrypted()
        # img_encrypted = self.connect_chunks_encrypted()
        img_out = np.array(self.data_hex_list_conn_enc_1)
        img_out = np.array(img_out)
        img_out = np.pad(img_out, (0, 2120 * 2120 - len(img_out)), 'constant')
        img_out = img_out.reshape(2120, 2120)
        img_out = img_out.astype(np.uint8)
        imwrite('obraz_zakodowany_crypto.tif', img_out, photometric='minisblack')

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

    def show_img(self, strips):
        kdx = 0
        for i in range(self.dic_values['length']):
            for j in range(self.dic_values['width']):
                self.img[i][j] = int(strips[kdx], 16)
                kdx += 1
        plt.imshow(self.img, cmap='gray')
        plt.show()

    # rsa encyption using exp mod
    def rsa_encrypt(self):
        self.data_hex_list_div_enc = ['0'] * int(len(self.all_strips) / self.len_of_m + 1)
        for idx, chunk in enumerate(self.data_hex_list_div):
            self.data_hex_list_div_enc[idx] = \
                self.public_key.encrypt(chunk, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                     algorithm=hashes.SHA256(), label=None))

    # divides a stream of bytes into a list of substreams
    def divide_to_chunks(self, chunk_len):
        self.data_hex_list_div = [self.all_strips[i:i + chunk_len] for i in range(0, len(self.all_strips), chunk_len)]
        for idx, chunk in enumerate(self.data_hex_list_div):
            self.data_hex_list_div[idx] = return_sum_enc(chunk)

    def generate_keys(self):
        self.private_numbers = rsa.RSAPrivateNumbers(p=self.p, q=self.q, d=self.d, dmp1=self.d % (self.p-1),
                                                     dmq1=self.d % (self.q-1), iqmp=pow(self.q, -1, self.p),
                                                     public_numbers=rsa.RSAPublicNumbers(self.e, self.n))
        self.private_key = self.private_numbers.private_key()
        self.public_key = self.private_key.public_key()

    def connect_chunks_encrypted(self):
        self.data_hex_list_conn_enc_1 = [0 for x in range(len(self.data_hex_list_div_enc) * 128)]
        print(len(self.data_hex_list_conn_enc_1))
        kdx = 0
        for chunk in self.data_hex_list_div_enc:
            for c in chunk:
                self.data_hex_list_conn_enc_1[kdx] = c
                kdx+=1