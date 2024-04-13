temp_humid = []
row = []
row.append(timestamp)
for i in range(3):
    while True:
        try:
            temperature = dht.temperature
            humidity = dht.humidity
            break
        except RuntimeError as e:
            # Reading doesn't always work! Just print error and we'll try again
            print("Reading from DHT failure: ", e.args)
    row.append("{:.1f}, {}".format(temperature,humidity))
    time.sleep(1)
temp_humid.append(row)
np.savetxt("temp_data.csv",
    temp_humid,
    delimiter =", ",
    fmt ='% s')
