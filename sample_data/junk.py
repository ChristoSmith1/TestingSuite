path = "C:\dev\playground\TestingSuite\sample_data\moon_2024_01_06_px6.txt"

with open(path, "r", encoding="utf8") as file:
    lines = [x.rstrip("\n") for x in file.readlines()]

new_lines = []

for line in lines:
    print(line)
    tokens = line.split()
    tokens.insert(0, "123 ")
    tokens.insert(0, "2024")
    tokens[2] = tokens[2] + ":00.000000    "
    el_token = f"{float(tokens[3]):0.5f} "
    az_token = f"{float(tokens[4]):0.5f}     "

    tokens[3] = az_token
    tokens[4] = el_token
    tokens.pop()

    new_line = " ".join(tokens)
    new_lines.append(new_line)

print("----------------")
print(repr(new_lines[-1]))

text = "\n".join(new_lines)
with open(path + "new", "w", encoding="utf8") as file:
    file.write(text)