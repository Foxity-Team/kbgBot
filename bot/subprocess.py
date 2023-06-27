import subprocess

proc = subprocess.Popen(["python", "-c", "import writer; writer.write()"], stdout=subprocess.PIPE)
out = proc.stdout.read()
with open('logs.txt', 'wb') as f:
    f.write(out)
