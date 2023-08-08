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

def decode_imu(file):
    with open(file, 'r') as f:
        data_points = f.readlines()
    with open(file+".out_imu", 'a+') as f:
        for i in data_points:
            if len(i) > 2:
                bin = binascii.a2b_base64(i)
                time = int(struct.unpack(">i", bytes([0, bin[0], bin[1], bin[2]]))[0]) / 1000
                gx = int(struct.unpack(">h", bytes([bin[4], bin[3]]))[0]) * 17.5
                gy = int(struct.unpack(">h", bytes([bin[6], bin[5]]))[0]) * 17.5
                gz = int(struct.unpack(">h", bytes([bin[8], bin[7]]))[0]) * 17.5
                ax = int(struct.unpack(">h", bytes([bin[10], bin[9]]))[0]) * 0.488
                ay = int(struct.unpack(">h", bytes([bin[12], bin[11]]))[0]) * 0.488
                az = int(struct.unpack(">h", bytes([bin[14], bin[13]]))[0]) * 0.488

                f.write(f"{time}, {gx}, {gy}, {gz}, {ax}, {ay}, {az}\n")
                #print(f"{time}, {gx}, {gy}, {gz}, {ax}, {ay}, {az}")
      
decode_imu("log_imu_wills")
