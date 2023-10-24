import sys

if __name__ == "__main__":
    lines = []
    
    single_table = {
        "add": """@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M+D""",


        "sub": """@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=M-D""",


        "gt": """@SP
A=M-1
D=M
@SP
M=M-1
A=M-1
D=M-D
M=0
@END_GT_{i}
D; JLE
@SP
A=M-1
M=-1
(END_GT_{i})""",

        "lt": """@SP
A=M-1
D=M
@SP
M=M-1
A=M-1
D=M-D
M=0
@END_LT_{i}
D; JGE
@SP
A=M-1
M=-1
(END_LT_{i})""",

        "eq": """@SP
A=M-1
D=M
@SP
M=M-1
A=M-1
D=M-D
M=0
@END_EQ_{i}
D; JNE
@SP
A=M-1
M=-1
(END_EQ_{i})""",

        "neg": """@SP
A=M-1
M=-M""",

        "or": """@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=D|M""",

        "not": """@SP
A=M-1
M=!M""",

        "and": """@SP
M=M-1
A=M
D=M
@SP
A=M-1
M=D&M"""

    }

    push_pop_table = {
        "push": {
            "constant": """@{i}
D=A
@SP
A=M
M=D
@SP
M=M+1""",


            "local": """@{i}
D=A
@LCL
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1""",


            "pointer": """@{i}
D=M
@SP
A=M
M=D
@SP
M=M+1""",
            "temp": """@{i}
D=M
@SP
A=M
M=D
@SP
M=M+1""",


            "argument": """@{i}
D=A
@ARG
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1""",


            "this": """@{i}
D=A
@THIS
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1""",


            "that": """@{i}
D=A
@THAT
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1""",

            "static": """@{filename}.{i}
D=M
@SP
A=M
M=D
@SP
M=M+1
"""

        },
        "pop": {
            "local": """@{i}
D=A
@LCL
D=M+D
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D""",


            "pointer": """@SP
M=M-1
A=M
D=M
@{i}
M=D""",
            "temp": """@SP
M=M-1
A=M
D=M
@{i}
M=D""",


            "argument": """@{i}
D=A
@ARG
D=M+D
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D""",


            "this": """@{i}
D=A
@THIS
D=M+D
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D""",


            "that": """@{i}
D=A
@THAT
D=M+D
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D""",


            "static": """@SP
M=M-1
A=M
D=M
@{filename}.{i}
M=D"""
        }
    }

    goto_table = {
        "label": """({filename}.{label})""",
        "if-goto": """@SP\nM=M-1\nA=M\nD=M\n@{filename}.{label}\nD; JNE\n""",
        "goto": """@{filename}.{label}\n0; JMP\n"""
    }
    with open(sys.argv[1]) as file:
        for line in file:
            if line.startswith("//") or line == "\n":
                continue
            index = line.find("//")
            if index != -1:
                line = line[:index]
            line = line.strip()
            lines.append(line)
    with open(sys.argv[1].split(".")[0] + ".asm", "w") as file:
        for index, line in enumerate(lines):
            file.write(f'// {line}\n')
            if len(line.split()) == 1:
                file.write(single_table[line.split()[0]].format(i=index))
            elif len(line.split()) == 2:
                file.write(goto_table[line.split()[0]].format(label=line.split()[1], filename=sys.argv[1].split(".")[0].split("/")[-1]))
            else:
                if (line.split()[1] == "temp"):
                    file.write(push_pop_table[line.split()[0]][line.split()[1]].format(i=int(line.split()[2])+5))
                elif (line.split()[1] == "pointer"):
                    file.write(push_pop_table[line.split()[0]][line.split()[1]].format(i=int(line.split()[2])+3))
                else:
                    file.write(push_pop_table[line.split()[0]][line.split()[1]].format(i=line.split()[2], filename=sys.argv[1].split(".")[0].split("/")[-1]))
            file.write("\n\n")
