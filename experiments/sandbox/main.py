import subprocess
import time

print("Executing main.py")

command = "python3 backgroundcheck.py &"
args = command.split()
#subprocess.call(command, shell=True)
subprocess.Popen(args)

for i in range(5):
    print("coming from main.py " + str(i))
    time.sleep(.5)



