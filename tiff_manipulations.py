class Tiff_manipulations(object):
    def __init__(self, file_name):
        self.dic_headers = {'width': 0x0100, 'length': 0x0101, 'bits_per_sample': 0x102, 'compression': 0x0103,
                            'photometric_interpretation': 0x0106, 'strip_offsets': 0x0111, 'samples_per_pixel': 0x115,
                            'rows_per_strip': 0x0116, 'strip_byte_counts': 0x0117, 'x_resolution': 0x011A,
                            'y_resolution': 0x011B, 'resolution_unit': 0x0128, 'artist': 0x013B, 'cell_length': 0x0109,
                            'cell_width': 0x0108, 'color_map': 0x0140, 'copyright': 0x8298, 'date_time': 0x132, 'extra_samples': 0x0152,
                            'fill_order': 0x010A, 'free_byte_counts': 0x0121, 'free_offsets:': 0x0120,
                            'gray_response_curve': 0x0123, 'gray_response_unit': 0x0122, 'host_computer': 0x013C,
                            'image_description': 0x010E, 'make': 0x010F, 'max_sample_value': 0x0119,
                            'min_sample_value': 0x0118, 'model': 0x0110, 'new_subfile_type': 0x00FE,
                            'orientation': 0x0112, 'planar_configuration': 0x011C, 'software': 0x0131,
                            'sub_file_type': 0x00FF, 'thresholding': 0x0107}

        self.list_req_fields = ['width', 'length', 'bits_per_sample', 'compression',
                            'photometric_interpretation', 'strip_offsets', 'rows_per_strip',
                            'strip_byte_counts', 'x_resolution', 'y_resolution', 'resolution_unit']

        self.dic_values = {'width': -2, 'length': -2, 'bits_per_sample': -2, 'compression': -2,
                            'photometric_interpretation': -2, 'strip_offsets': -2, 'samples_per_pixel': -2,
                            'rows_per_strip': -2, 'strip_byte_counts': -2, 'x_resolution': -2, 'y_resolution': -2,
                            'resolution_unit': -2, 'artist': -2, 'cell_length': -2, 'cell_width': -2,
                            'color_map': -2, 'copyright': -2, 'date_time': -2, 'extra_samples': -2,
                            'fill_order': -2, 'free_byte_counts': -2, 'free_offsets:': -2, 'gray_response_curve': -2,
                            'gray_response_unit': -2, 'host_computer': -2, 'image_description': -2, 'make': -2,
                            'maxSampleValue': -2, 'minSampleValue': -2, 'model': -2, 'newSubfileType': -2,
                            'orientation': -2, 'planar_configuration': -2, 'software': -2, 'sub_file_type': -2,
                            'thresholding': -2}

        self.str_hex = self.read_return_hex(file_name)
        self.data_hex_list = self.str_to_hexlist(self.str_hex)
        self.byte_order = self.return_byte_order()
        self.is_file_tiff = self.is_file_tiff()

        self.offset_1 = self.return_1_offset()
        self.number_of_dic_entr = int(self.return_sum(self.data_hex_list[self.offset_1 : self.offset_1 + 2]), 16)
        self.main_header = self.offset_1 + 2
        self.hexrange = self.main_header + 12 * self.number_of_dic_entr

    def check_required_fields(self):
        for req_field in self.list_req_fields:
            if self.dic_values[req_field] == -2:
                return False
        return True

    def return_1_offset(self):
        header = int('0x0004', 16)
        sum_of_elem = int(self.return_sum(self.data_hex_list[header: header + 4]), 16)
        return sum_of_elem

    def check_header(self, header):
        return int(self.return_sum(self.data_hex_list[header: header + 2]), 16)

    def check_number_of_values(self, header):
        return int(self.return_sum(self.data_hex_list[header + 4: header + 8]), 16)

    def list_data(self):
        dictionary = vars(self)
        for element in dictionary.items():
            if type(element[1]) is int or type(element[1]) is bool or type(element[1]) is tuple:
                print(element)
        for ele in self.dic_values.items():
            if ele[1] != -2:
                print(ele[0], ":", ele[1])

    def find_key(self, header):
        for element in self.dic_headers:
            if self.dic_headers[element] == header:
                return element
        return -1

    def read_data(self, mod=0):
        if mod == 0:
            for header in range(self.main_header, self.hexrange, 12):
                key = self.find_key(self.check_header(header))
                if key != -1:
                    self.dic_values[key] = self.proper_type_place(header)
        elif mod == 1:
            for header in range(self.main_header, self.hexrange, 12):
                key = self.find_key(self.check_header(header))
                if key != -1:
                    if self.is_ascii(header) is True:
                        self.dic_values[key] = self.delete_ascii(header)

    def return_byte_order(self):
        header = int('0x0000', 16)
        sum_of_elem = self.data_hex_list[header] + self.data_hex_list[header + 1]
        # little-endian
        if int(sum_of_elem, 16) == 0x4949:
            return 0
        # big-endian
        elif int(sum_of_elem, 16) == 0x4d4d:
            return 1
        # error
        else:
            return -1

    def return_sum(self, vector):
        sum_of_elem = ''
        if self.byte_order == 1:
            for i in range(0, len(vector)):
                sum_of_elem = sum_of_elem + vector[i]
        elif self.byte_order == 0:
            for i in range(len(vector) - 1, -1, -1):
                sum_of_elem = sum_of_elem + vector[i]
        return sum_of_elem

    def read_return_hex(self, file_name):
        file = open(file_name, "rb")
        data = file.read()
        file.close()
        data_hex = data.hex()
        return data_hex

    def str_to_hexlist(self, s):
        data_hex_list = []
        for i in range(len(s)):
            if i % 2 == 0 and i != 0:
                data_hex_list.append(s[i - 2:i])
        return data_hex_list

    def is_file_tiff(self):
        header = int('0x0002', 16)
        sum_of_elem = int(self.return_sum(self.data_hex_list[header: header + 2]), 16)
        if sum_of_elem == 0x002A:
            return True
        else:
            return False

    def check_type(self, header):
        type_of_var = int(self.return_sum(self.data_hex_list[header + 2: header + 4]), 16)
        return type_of_var

    def proper_type_place(self, header):
        chunk_type = self.check_type(header)
        number_of_values = self.check_number_of_values(header)
        if number_of_values == 1:
            if chunk_type == 0x0001:
                return int(self.return_sum(self.data_hex_list[header + 8: header + 9]), 16)
            if chunk_type == 0x0002:
                return chr(int(self.return_sum(self.data_hex_list[header + 8: header + 9]), 16))
            if chunk_type == 0x0003:
                return int(self.return_sum(self.data_hex_list[header + 8: header + 10]), 16)
            if chunk_type == 0x0004:
                return int(self.return_sum(self.data_hex_list[header + 8: header + 12]), 16)
            if chunk_type == 0x0005:
                header_copy = int(self.return_sum(self.data_hex_list[header + 8: header + 12]), 16)
                return (int(self.return_sum(self.data_hex_list[header_copy: header_copy + 4]), 16), "/",
                       int(self.return_sum(self.data_hex_list[header_copy + 4: header_copy + 8]), 16))
            else:
                return -1

        if number_of_values == 2 and chunk_type in (0x0001, 0x0002, 0x0003):
            if chunk_type == 0x0001:
                return (int(self.return_sum(self.data_hex_list[header + 8: header + 9]), 16),
                        int(self.return_sum(self.data_hex_list[header + 9: header + 10]), 16))
            if chunk_type == 0x0002:
                data_array = []
                for i in range(number_of_values - 1):
                    data_array.append(chr(int(self.return_sum(self.data_hex_list[header + 8 + i: header + 9 + i]), 16)))
                return ''.join(data_array)
            if chunk_type == 0x0003:
                return (int(self.return_sum(self.data_hex_list[header + 8: header + 10]), 16),
                        int(self.return_sum(self.data_hex_list[header + 10: header + 12]), 16))
            else:
                return -1

        if number_of_values == 3 and chunk_type in (0x0001, 0x0002):
            if chunk_type == 0x0001:
                return (int(self.return_sum(self.data_hex_list[header + 8: header + 9]), 16),
                        int(self.return_sum(self.data_hex_list[header + 9: header + 10]), 16),
                        int(self.return_sum(self.data_hex_list[header + 10: header + 11]), 16))
            if chunk_type == 0x0002:
                data_array = []
                for i in range(number_of_values - 1):
                    data_array.append(chr(int(self.return_sum(self.data_hex_list[header + 8 + i: header + 9 + i]), 16)))
                return ''.join(data_array)
            else:
                return -1

        if number_of_values == 4 and chunk_type in (0x0001, 0x0002):
            if chunk_type == 0x0001:
                return (int(self.return_sum(self.data_hex_list[header + 8: header + 9]), 16),
                        int(self.return_sum(self.data_hex_list[header + 9: header + 10]), 16),
                        int(self.return_sum(self.data_hex_list[header + 10: header + 11]), 16),
                        int(self.return_sum(self.data_hex_list[header + 11: header + 12]), 16))
            if chunk_type == 0x0002:
                data_array = []
                for i in range(number_of_values - 1):
                    data_array.append(chr(int(self.return_sum(self.data_hex_list[header + 8 + i: header + 9 + i]), 16)))
                return ''.join(data_array)
            else:
                return -1

        else:
            data_array = []
            if chunk_type == 0x0001:
                header_copy = int(self.return_sum(self.data_hex_list[header + 8: header + 12]), 16)
                for i in range(number_of_values):
                    data_array.append(int(self.return_sum(self.data_hex_list[header_copy + i: header_copy + i + 1]), 16))
                return data_array

            if chunk_type == 0x0002:
                header_copy = int(self.return_sum(self.data_hex_list[header + 8: header + 12]), 16)
                for i in range(number_of_values - 1):
                    data_array.append(chr(int(self.return_sum(self.data_hex_list[header_copy + i: header_copy + i + 1]), 16)))
                return ''.join(data_array)

            if chunk_type == 0x0003:
                number_of_values = 2 * number_of_values
                header_copy = int(self.return_sum(self.data_hex_list[header + 8: header + 12]), 16)
                for i in range(0, number_of_values, 2):
                    data_array.append(int(self.return_sum(self.data_hex_list[header_copy+i: header_copy+i+2]), 16))
                return data_array

            if chunk_type == 0x0004:
                number_of_values = 4 * number_of_values
                header_copy = int(self.return_sum(self.data_hex_list[header + 8: header + 12]), 16)
                for i in range(0, number_of_values, 4):
                    data_array.append(int(self.return_sum(self.data_hex_list[header_copy+i: header_copy+i+4]), 16))
                return data_array
            else:
                return -1

    def is_ascii(self, header):
        chunk_type = self.check_type(header)
        number_of_values = self.check_number_of_values(header)
        if number_of_values == 1:
            if chunk_type == 0x0002:
                return True
        else:
            if chunk_type == 0x0002:
                return True
        return False

    def delete_ascii(self, header):
        chunk_type = self.check_type(header)
        number_of_values = self.check_number_of_values(header)
        if number_of_values in (1, 2, 3, 4):
            if chunk_type == 0x0002:
                for i in range(number_of_values-1):
                    self.data_hex_list[header + i + 8] = '00'
                return "delete"
        else:
            if chunk_type == 0x0002:
                header_copy = int(self.return_sum(self.data_hex_list[header + 8: header + 12]), 16)
                for i in range(number_of_values-1):
                    self.data_hex_list[header_copy + i] = '00'
                return "delete"