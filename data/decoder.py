import binascii
import struct

def decode_pres(file):
    with open(file, 'r') as f:
        data_points = f.readlines()
    bin_1 = binascii.a2b_base64(data_points[0])
    start_pressure = struct.unpack(">i", bytes([0, bin_1[5], bin_1[4], bin_1[3]]))[0]
    print(start_pressure)
    with open(file+".out", 'a+') as f:
        for i in data_points:
            if len(i) > 2:
                bin = binascii.a2b_base64(i)
                time = int(struct.unpack(">i", bytes([0, bin[0], bin[1], bin[2]]))[0]) / 1000
                pressure = struct.unpack(">i", bytes([0, bin[5], bin[4], bin[3]]))[0]
                temp = int(struct.unpack(">h", bytes([bin[7], bin[6]]))[0])/100
                f.write(f"{time}, {pressure}, {temp}\n")
      
decode_pres("log_pres_wills")
