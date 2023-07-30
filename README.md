# RpiFly Software & Data
Formats:
    Pressure logs -> 3 bytes time in ms, 3 bytes pressure with 4096 LSB/hPa (swap order then its MSB), 2 bytes temperature with 100 LSB/celcius (swap order then its MSB)
    IMU logs -> 3 bytes time in ms, 2 bytes for all gyro x, y, z (17.5 mdps/LSB) then acclerometer x, y, z (0.488 mg/LSB). 