import gf
import zlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import binascii


class Entry:
    def __init__(self):
        self.offset = 0
        self.data_length = 0
        self.bitflag = 0x0
        self.out_data = b''


def decrypt_block(block_bin):
    key = binascii.unhexlify('9DC7A1C64DC8FC377D6085DE22760DA0A594D231770C5B10DBD0DBF47628EEDD')
    cipher = AES.new(key, mode=AES.MODE_ECB)

    # Padding produces incorrect data for the last bytes if it is padded.
    padded_block_bin = pad(block_bin, 16)
    plaintext = cipher.decrypt(padded_block_bin)[:len(block_bin)]

    return plaintext


def parse_entry_table(fb):
    """
    Entry table
    for pakchunk08_s00_ja-WindowsNoEditor.pak starts at 0x1957A50
    Stride 0x18/24

    0x0 uint32 offset
    0x8 uint32 byte length
    0xE uint8 bitflag

    bitflag is probably compressed/encryption flag, with the data from 0x10 -> 0x18 being related to that
    0x4 flag and 0x14 flag

    0x10 is probably encrypted, 0x4 is compressed

    Compression could be oodle or zlib
    """
    offset = 0x1957A50
    count = gf.get_uint32(fb, 0x19579C0)
    entries = []
    for i in range(offset, offset+count*0x18, 0x18):
        entry = Entry()
        entry.data_offset = gf.get_uint32(fb, i) + 0x18
        entry.data_length = gf.get_uint32(fb, i+0x8)
        entry.bitflag = fb[i+0xE]
        entries.append(entry)
    return entries


def parse_names(fb):
    offset = 0x195D5F8
    end_offset = 0x195E318
    name_offsets = []
    for i in range(offset, end_offset, 8):
        name_offsets.append(gf.get_uint16(fb, i))
    names = []
    offset = 0x195AA88
    for i in range(len(name_offsets)-1):
        length = name_offsets[i+1]-name_offsets[i]
        o = offset + name_offsets[i]
        names.append(fb[o:o+length].decode('ascii'))
    return names


def get_entries(fb, entries):
    for i, entry in enumerate(entries):
        encrypted_data = fb[entry.data_offset:entry.data_offset+entry.data_length]
        with open(f'test_out/{file[:-4]}_{i}.bin', 'wb') as f:
            # Decrypt
            if entry.bitflag & 0x4:
                compressed_data = decrypt_block(encrypted_data)
            else:
                compressed_data = encrypted_data

            if entry.bitflag & 0x10:
                # Decompress
                # Removing padding
                if len(compressed_data) % 16 == 0:
                    similarity = 0
                    for k in range(1, len(compressed_data)):
                        if compressed_data[k] == compressed_data[similarity]:
                            similarity += 1
                        else:
                            similarity = 0
                if similarity:
                    compressed_data = compressed_data[:-similarity]
                try:
                    entry.out_data = zlib.decompress(compressed_data)
                except:
                    print(f'Broken at {i}. Writing uncompressed instead...')
                    entry.out_data = compressed_data
            else:
                entry.out_data = compressed_data

            f.write(entry.out_data)

        print(i)


def unpack(pak):
    fb = open(pak, 'rb').read()
    entries = parse_entry_table(fb)
    # names = parse_names(fb)
    get_entries(fb, entries)


if __name__ == '__main__':
    path = 'C:\Program Files (x86)\Steam\steamapps\common\OUTRIDERS Demo\Madness\Content\Paks/'
    file = 'pakchunk15_s00_UI-WindowsNoEditor.pak'

    unpack(path + file)
