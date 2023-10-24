import sys, os

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

    func_table = {
        "start": """@256
D=A
@SP
M=D
@{filename}.start$ret.0 // push return address
D=M
@SP
A=M
M=D
@SP
M=M+1

@LCL
D=A
@SP
A=M
M=D
@SP
M=M+1

@ARG
D=A
@SP
A=M
M=D
@SP
M=M+1

@THIS
D=A
@SP
A=M
M=D
@SP
M=M+1

@THAT
D=A
@SP
A=M
M=D
@SP
M=M+1

@5 //calculate ARGs position
D=A
@SP
D=M-D
@ARG
M=D

@SP
D=A
@LCL
M=D

@Sys.init
0; JMP
({filename}.start$ret.0)
""",
"return": """@LCL
D=M
@frame.{filename}.{function_name}.{i}
M=D
@5
D=A
@frame.{filename}.{function_name}.{i}
D=M-D
@ret.{filename}.{function_name}.{i}
M=D
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
D=A
@SP
M=D+1
@frame.{filename}.{function_name}.{i}
A=M-1
D=M
@THAT
M=D
@frame.{filename}.{function_name}.{i}
A=M-1
A=A-1
D=M
@THIS
M=D
@frame.{filename}.{function_name}.{i}
A=M-1
A=A-1
A=A-1
D=M
@ARG
M=D
@frame.{filename}.{function_name}.{i}
A=M-1
A=A-1
A=A-1
A=A-1
D=M
@LCL
M=D
@ret.{filename}.{function_name}.{i}
A=M
0; JMP
""",
"function": """({filename}.{function_name})
{locals_push}
""",
"call": """@{filename}.{function_name}$ret.{i} // push return address
D=M
@SP
A=M
M=D
@SP
M=M+1

@LCL
D=A
@SP
A=M
M=D
@SP
M=M+1

@ARG
D=A
@SP
A=M
M=D
@SP
M=M+1

@THIS
D=A
@SP
A=M
M=D
@SP
M=M+1

@THAT
D=A
@SP
A=M
M=D
@SP
M=M+1

@{nArgs_shift} //calculate ARGs position
D=A
@SP
D=M-D
@ARG
M=D

@SP
D=A
@LCL
M=D

@{filename}.{goto_function_name}
0; JMP
({filename}.{function_name}$ret.{i})
"""
    }

    func_stack = []
    if not os.path.isdir(sys.argv[1]):
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
            # file.write(func_table["start"].format(filename=sys.argv[1].split(".")[0].split("/")[-1]))
            for index, line in enumerate(lines):
                file.write(f'// {line}\n')
                if len(line.split()) == 1:
                    if line.split()[0] == "return":
                        file.write(func_table[line.split()[0]].format(i=index, filename=sys.argv[1].split(".")[0].split("/")[-1], function_name=func_stack[-1]))
                        func_stack.pop()
                    else:
                        file.write(single_table[line.split()[0]].format(i=index))
                elif len(line.split()) == 2:
                    file.write(goto_table[line.split()[0]].format(label=line.split()[1], filename=sys.argv[1].split(".")[0].split("/")[-1]))
                else:
                    if line.split()[0] == "function":
                        func_stack.append(line.split()[1])
                        file.write(func_table[line.split()[0]].format(filename=sys.argv[1].split(".")[0].split("/")[-1], function_name=line.split()[1], locals_push="\n".join(list([push_pop_table["push"]["constant"].format(i=0) + "\n" + push_pop_table["pop"]["local"].format(i=i) for i in range(int(line.split()[2]))]))))
                    elif (line.split()[1] == "temp"):
                        file.write(push_pop_table[line.split()[0]][line.split()[1]].format(i=int(line.split()[2])+5))
                    elif (line.split()[1] == "pointer"):
                        file.write(push_pop_table[line.split()[0]][line.split()[1]].format(i=int(line.split()[2])+3))
                    else:
                        file.write(push_pop_table[line.split()[0]][line.split()[1]].format(i=line.split()[2], filename=sys.argv[1].split(".")[0].split("/")[-1]))
                file.write("\n\n")
