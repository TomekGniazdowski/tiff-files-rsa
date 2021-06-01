import math
import random
import secrets
import matplotlib.pyplot as plt
import numpy as np
import sympy
from tifffile.tifffile import imwrite
import tiff_manipulations as tm


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


class TiffEncrypting_counter(tm.Tiff_manipulations):
    def __init__(self, file_name):
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
        self.e = 65537
        self.n = -1
        self.d = -1
        self.len_of_m = -1
        self.nonce = -1
        self.len_of_nonce = -1
        self.len_of_counter = -1
        self.generate_keys()


        print('e:', self.e, 'n:', self.n, 'd:', self.d, 'dlugosc m:', self.len_of_m)
        self.data_hex_list_div_int = [0] * (int((len(self.all_strips) / self.len_of_m)) + 1)
        # all stripes, divided, int, encrypted

        # dividing
        self.inputlist = []
        self.generate_nonce()

        self.generate_input()
        # RSA
        self.inputlist_enc = [0] * len(self.inputlist)
        self.rsa_encrypt()
        self.data_hex_list_div_int = [0] * (int((len(self.all_strips) / self.len_of_m)) + 1)
        self.divide_to_chunks(chunk_len=self.len_of_m)
        self.list_xored = [0] * len(self.inputlist)
        self.generate_xor()
        shiet = 2
        img_encrypted = self.connect_chunks_encrypted()
        img_out = np.array(img_encrypted)
        img_out = convert_list_hex_int(img_out)
        img_out = np.array(img_out)
        img_out = np.pad(img_out, (0, 1017 * 1016 - len(img_out)), 'constant')
        img_out = img_out.reshape(1017, 1016)
        img_out = img_out.astype(np.uint8)
        imwrite('obraz_zakodowany_counter.tif', img_out, photometric='minisblack')

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
        idx = 0
        for chunk in self.inputlist:
            self.inputlist_enc[idx] = pow(chunk, self.e, self.n)
            idx += 1
        # print('zakodowany:', self.data_hex_list_div_int_enc)

    # divides a stream of bytes into a list of substreams
    def divide_to_chunks(self, chunk_len):
        self.data_hex_list_div = [self.all_strips[i:i + chunk_len] for i in range(0, len(self.all_strips), chunk_len)]
        for idx, chunk in enumerate(self.data_hex_list_div):
            self.data_hex_list_div[idx] = return_sum_enc(chunk)
        # print('podzielony:', self.data_hex_list_div)
        for idx, chunk in enumerate(self.data_hex_list_div):
            self.data_hex_list_div_int[idx] = int(chunk, 16)
        # print('podzielony, int:', self.data_hex_list_div_int)

    def generate_keys(self):
        # state number of bits per p and q
        num_of_bits = random.randrange(450, 550)
        # random numbers of given number of bits
        p = secrets.randbits(num_of_bits)
        q = secrets.randbits(1016 - num_of_bits)
        # try as long as they are not prime
        while sympy.isprime(p) is False:
            p = secrets.randbits(num_of_bits)
        while sympy.isprime(q) is False:
            q = secrets.randbits(1016 - num_of_bits)
        self.n = p * q
        phi_n = (p - 1) * (q - 1)
        # exp mod
        self.d = pow(self.e, -1, phi_n)
        # get bit length of n
        bit_len_of_n = int((math.log(self.n) / math.log(2)) + 1)
        # make sure m is not longer than n
        bit_len_of_m = bit_len_of_n - 1
        self.len_of_m = bit_len_of_m // 8 + 1


    def generate_nonce(self):

        self.nonce = secrets.token_hex(120)
        self.len_of_nonce = 120
        self.len_of_counter = 12

    def generate_input(self):
        for i in range(len(self.data_hex_list_div_int)):
            counter = hex(i)[2:]
            if len(counter) < self.len_of_counter:
                first_zeros = '0' * (self.len_of_counter - len(counter))
                counter = first_zeros+counter
            lang = int((self.nonce + counter), 16).bit_length()
            self.inputlist.append(int((self.nonce+counter), 16))

    def generate_xor(self):
        for i in range(len(self.data_hex_list_div_int)):
            chunk = str(bin(self.data_hex_list_div_int[i]))[2:].zfill(1016)
            encryptedinput = str(bin(self.inputlist_enc[i]))[2:].zfill(1016)
            y = int(chunk, 2) ^ int(encryptedinput, 2)
            self.list_xored[i] = int(bin(y)[2:].zfill(len(chunk)), 2)

    def connect_chunks_encrypted(self):
        # print(self.data_hex_list_div_int_enc)
        self.how_inc = 0
        self.data_hex_list_conn_enc_1 = ['0' for x in range(len(self.list_xored))]
        for idx, chunk in enumerate(self.list_xored):
            self.data_hex_list_conn_enc_1[idx] = hex(chunk).replace('0x', '')
        # print('zakodowany, hex:', self.data_hex_list_conn_enc_1)

        self.data_hex_list_conn_enc_2 = ['0' for x in range(len(self.data_hex_list_conn_enc_1) * (self.len_of_m))]
        kdx = 0
        for idx, chunk in enumerate(self.data_hex_list_conn_enc_1):
            if len(chunk) < self.len_of_m * 2 and idx != (len(self.data_hex_list_conn_enc_1) - 1):
                first_zeros = '0' * (self.len_of_m * 2 - len(chunk))
                chunk = first_zeros + chunk
            if len(chunk) % 2 != 0:
                chunk = '0' + chunk
            for jdx in range(0, len(chunk), 2):
                c = chunk[jdx:jdx + 2]
                if len(c) == 2:
                    self.data_hex_list_conn_enc_2[kdx] = c
                    kdx += 1
        # print('zakodowany, podzielony na piksele, hex:', self.data_hex_list_conn_enc_2)
        return self.data_hex_list_conn_enc_2
