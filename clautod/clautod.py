import time
while(1):
    time.sleep(1)
    with open("/home/jeremy/Projects/Clauto/HELLO.sh", "w") as file:
        file.write("Hello I am clautod\n")