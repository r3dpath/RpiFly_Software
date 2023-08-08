import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
csv_file_path = 'log_imu_wills.out_imu'  # Replace with the actual path to your CSV file
data = pd.read_csv(csv_file_path)

# Extract data columns
time = data['time'][176000:195000]
gyroscope_data = data[['gx', 'gy', 'gz']][176000:195000]
accelerometer_data = data[['ax', 'ay', 'az']][176000:195000]

# Plot gyroscope data
plt.figure(figsize=(10, 6))
plt.plot(time, gyroscope_data)
plt.title('Gyroscope Data vs Time')
plt.xlabel('Time')
plt.ylabel('Angular Rate')
plt.legend(['gx', 'gy', 'gz'])
plt.grid()
plt.show()

# Plot accelerometer data
plt.figure(figsize=(10, 6))
plt.plot(time, accelerometer_data)
plt.title('Accelerometer Data vs Time')
plt.xlabel('Time')
plt.ylabel('Acceleration')
plt.legend(['ax', 'ay', 'az'])
plt.grid()
plt.show()