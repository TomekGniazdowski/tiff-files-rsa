import tiff_decrypting as td
import tiff_encrypting as te
import tiff_encrypting_crypto as teco
import tiff_decrypting_counter as tdc
import tiff_encrypting_counter as tec
import tiff_decrypting_crypto as tdco
if __name__ == '__main__':
    o = 'dzielox12.tif'
    enc = te.TiffEncrypting(o)
    dec = td.TiffDecrypting('obraz_zakodowany.tif', enc.len_of_m + 1, enc.n, enc.d)
    enc_crypto = teco.TiffEncryptingcrypto(o, enc.n, enc.e, enc.d, enc.p, enc.q, enc.len_of_m)
    dec_crypto = tdco.TiffDecryptingcrypto('obraz_zakodowany_crypto.tif', enc_crypto.private_key)
    enc_ctr = tec.TiffEncrypting_counter(o)
    dec_ctr = tdc.TiffEncrypting_counter('obraz_zakodowany_counter.tif', enc_ctr.len_of_m, enc_ctr.n, enc_ctr.e, enc_ctr.nonce)