import subprocess
import glob
import os

# todo: use filename info to give duration, excluding breaks larger than a second (truncate them to a second)
# then, make a text file that has the frame location of these breaks

filenames = glob.glob("FRONTAL" + os.sep + '*.png')
this_path = os.path.abspath(".")
path = os.path.abspath("." + os.sep + "FRONTAL")
print(path)
fps = 30
duration = 1.0/fps

with open("ffmpeg_input.txt", "wb") as outfile:
    for filename in filenames:
        outfile.write(f"file '{this_path}{os.sep}{filename}'\n".encode())
        outfile.write(f"duration {duration}\n".encode())

command_line = f"ffmpeg -r {fps} -f concat -safe 0 -i .{os.sep}ffmpeg_input.txt -c:v libx265 -pix_fmt yuv420p {this_path}{os.sep}out.mp4"
print(command_line)

pipe = subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE).stdout
output = pipe.read().decode()
pipe.close()