import sys

if __name__ == "__main__":
    lines = []

    symbol_table = {
        "R0": 0,
        "R1": 1,
        "R2": 2,
        "R3": 3,
        "R4": 4,
        "R5": 5,
        "R6": 6,
        "R7": 7,
        "R8": 8,
        "R9": 9,
        "R10": 10,
        "R11": 11,
        "R12": 12,
        "R13": 13,
        "R14": 14,
        "R15": 15,
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
        "SCREEN": 16384,
        "KBD": 24576,
    }

    dest_table = {
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "AMD": "111",
    }

    comp_table = {
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "!D": "0001101",
        "!A": "0110001",
        "-D": "0001111",
        "-A": "0110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "D+A": "0000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D&A": "0000000",
        "D|A": "0010101",
        "M": "1110000",
        "!M": "1110001",
        "-M": "1110011",
        "M+1": "1110111",
        "M-1": "1110010",
        "D+M": "1000010",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&M": "1000000",
        "D|M": "1010101",
    }

    jmp_table = {
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }

    with open(sys.argv[1]) as file:
        i = 0
        for line in file:
            if line.startswith("//") or line == "\n":
                continue
            index = line.find("//")
            if index != -1:
                line = line[:index]
            line = line.strip()
            if line[0] == "(":
                symbol_table[line[1:-1]] = i
                continue
            lines.append(line)
            i += 1
    variable_address = 16
    with open(sys.argv[1].split(".")[0] + ".hack", "w") as file:
        for line in lines:
            if line[0] == "@":
                if line[1:].isdigit():
                    line = f"{int(line[1:]):016b}"
                elif symbol_table.get(line[1:]) != None:
                    line = f"{symbol_table[line[1:]]:016b}"
                else:
                    symbol_table[line[1:]] = variable_address
                    line = f"{variable_address:016b}"
                    variable_address += 1
            else:
                index = line.find("=")
                if index != -1:
                    dest = dest_table[line.split("=")[0]]
                    line = line.split("=")[1]
                else:
                    dest = "000"
                if ";" in line:
                    comp = comp_table[line.split(";")[0]]
                    jump = jmp_table[line.split(";")[1]]
                else:
                    comp = comp_table[line]
                    jump = "000"
                line = f"111{comp}{dest}{jump}"
            file.write(line+"\n")
