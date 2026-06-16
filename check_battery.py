from naoqi import ALProxy

mem = ALProxy("ALMemory", "127.0.0.1", 9559)

charge = mem.getData("Device/SubDeviceList/Battery/Charge/Sensor/Value")
print("Bateria: %.1f%%" % (charge * 100))