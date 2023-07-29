import re

file = open('dump_cone_launch.bin', 'rb').read()

matches = re.findall(r"(\w|\+|\/|\=){20}", file)
print(len(matches))