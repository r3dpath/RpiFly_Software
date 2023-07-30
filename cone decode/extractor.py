imu = open("imu_cone", "a")
pres = open("pres_cone", "a")
binin = open("dump_cone_launch copy.bin", "r")

lines = binin.readlines()

for line in lines:
    if len(line) == 13:
        pres.write(line)
    elif len(line) == 21:
        imu.write(line)

imu.close()
pres.close()
binin.close()