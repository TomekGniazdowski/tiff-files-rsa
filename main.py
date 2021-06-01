import tiff_decrypting as td
import tiff_encrypting as te
import tiff_decrypting_counter as tdc
import tiff_encrypting_counter as tec
if __name__ == '__main__':
    # enc = te.TiffEncrypting('Bez nazwy.tif')
    # dec = td.TiffDecrypting('obraz_zakodowany.tif', enc.len_of_m + 1, enc.n, enc.d)
    enc1 = tec.TiffEncrypting_counter('dzielox12.tif')
    dec1 = tdc.TiffEncrypting_counter('obraz_zakodowany_counter.tif', enc1.len_of_m, enc1.n, enc1.e, enc1.nonce)
