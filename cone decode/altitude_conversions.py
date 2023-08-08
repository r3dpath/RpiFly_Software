import numpy as np
import matplotlib.pyplot as plt



with open("pres_cone_crop.out", "r") as f:
    lines = f.readlines()


def zero(lines, to):
    pre_pressure = []
    for i in range(to):
        line = lines[i].split(", ")
        pre_pressure.append(int(line[1]))
    return sum(pre_pressure)/len(pre_pressure)

def altitude(pressure, temp, p0):
    return (((p0/pressure)**(1/5.257)-1)*(temp+273.15))/0.0065

P0 = zero(lines, 1000)
ts = []
alts = []
for line in lines:
    time, pressure, temp = line.split(', ')
    time = float(time)
    pressure = int(pressure)
    temp = float(temp)
    ts.append(time)
    alts.append(altitude(pressure, temp, P0))

print(max(alts))
plt.plot(ts, alts)
plt.title("Altitude Wills Launch")
plt.ylabel("Height(m)")
plt.xlabel("Time (s)")
plt.grid()
plt.show()