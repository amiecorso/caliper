import subprocess
import time

print("Executing main.py")

command = "python3 backgroundcheck.py &"
subprocess.call(command, shell=True)

for i in range(5):
    print("coming from main.py " + str(i))
    time.sleep(.5)



