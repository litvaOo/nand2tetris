import sys, os, glob
from pathlib import Path

select_two = """@SP
M=M-1
A=M
D=M
@SP
A=M-1

"""

calculate_difference = """@SP
M=M-1
A=M
D=M
A=A-1
D=M-D
M=0

"""

push_to_stack = """
@SP
M=M+1
A=M-1
M=D
"""

get_constant = "@{i}\nD=A\n"

select_segment = """@{segment}\nA=M+D\nD=M\n"""

pop_from_stack = """@SP\nM=M-1\nA=M\nD=M\n"""

void_local = "@{i}\nD=A\n@LCL\nA=M+D\nM=0\n@SP\nM=M+1"

if __name__ == "__main__":
    
    single_table = {
        "add": f"{select_two}M=M+D\n",


        "sub": f"{select_two}M=M-D\n",


        "gt": calculate_difference + """@END_GT_{i}
D; JLE
@SP
A=M-1
M=-1
(END_GT_{i})\n""",

        "lt": calculate_difference + """@END_LT_{i}
D; JGE
@SP
A=M-1
M=-1
(END_LT_{i})\n""",

        "eq": calculate_difference + """@END_EQ_{i}
D; JNE
@SP
A=M-1
M=-1
(END_EQ_{i})\n""",

        "and": f"{select_two}M=D&M\n",
        "or": f"{select_two}M=D|M\n",

        "neg": """@SP\nA=M-1\nM=-M\n""",
        "not": """@SP\nA=M-1\nM=!M\n""",
    }

    push_pop_table = {
        "push": {
            "constant": get_constant + push_to_stack,
            "local": get_constant + select_segment.format(segment="LCL") + push_to_stack,
            "argument": get_constant + select_segment.format(segment="ARG") + push_to_stack,
            "this": get_constant + select_segment.format(segment="THIS") + push_to_stack,
            "that": get_constant + select_segment.format(segment="THAT") + push_to_stack,
            "pointer": "@{i}\nD=M" + push_to_stack,
            "temp": "@{i}D=M" + push_to_stack,
            "static": "@{filename}.{i}\nD=M\n" + push_to_stack,
        },
        "pop": {
            "local": get_constant + """
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


            "argument": get_constant + """
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


            "this": get_constant + """
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


            "that": get_constant + """
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
D=A
@SP
A=M
M=D
@SP
M=M+1

@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1

@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1

@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1

@THAT
D=M
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
D=M
@LCL
M=D

@Sys.init
0; JMP
({filename}.start$ret.0)
""",
"return": """@LCL
D=M
@frame.{function_name}.{i}
M=D
@5
D=A
@frame.{function_name}.{i}
A=M-D
D=M
@ret.{function_name}.{i}
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
@frame.{function_name}.{i}
A=M-1
D=M
@THAT
M=D
@frame.{function_name}.{i}
A=M-1
A=A-1
D=M
@THIS
M=D
@3
D=A
@frame.{function_name}.{i}
A=M-D
D=M
@ARG
M=D
@4
D=A
@frame.{function_name}.{i}
A=M-D
D=M
@LCL
M=D
@ret.{function_name}.{i}
A=M
0; JMP
""",
"function": """({function_name})
{locals_push}
""",
"call": """@{function_name}$ret.{i} // push return address
D=A
@SP
A=M
M=D
@SP
M=M+1

@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1

@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1

@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1

@THAT
D=M
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
D=M
@LCL
M=D

@{goto_function_name}
0; JMP
({function_name}$ret.{i})
"""
    }

    func_stack = []

    def file_parse(filename):
        with open(filename) as file:
            lines = []
            for line in file:
                if line.startswith("//") or line == "\n":
                    continue
                index = line.find("//")
                if index != -1:
                    line = line[:index]
                line = line.strip()
                lines.append(line)
        result = [f"// {filename}\n"]
        for index, line in enumerate(lines):
                result.append(f'// {line}\n')
                if len(line.split()) == 1:
                    if line.split()[0] == "return":
                        result.append(func_table[line.split()[0]].format(i=index, filename=filename.split(".")[0].split("/")[-1], function_name=func_stack[-1]))
                        func_stack.pop()
                    else:
                        result.append(single_table[line.split()[0]].format(i=index))
                elif len(line.split()) == 2:
                    result.append(goto_table[line.split()[0]].format(label=line.split()[1], filename=filename.split(".")[0].split("/")[-1]))
                else:
                    if line.split()[0] == "function":
                        func_stack.append(line.split()[1])
                        result.append(func_table[line.split()[0]].format(filename=filename.split(".")[0].split("/")[-1], function_name=line.split()[1], locals_push="\n".join(list([void_local.format(i=i) for i in range(int(line.split()[2]))]))))
                    elif line.split()[0] == "call":
                        result.append(func_table[line.split()[0]].format(filename=filename.split(".")[0].split("/")[-1], function_name=func_stack[-1], i=index, goto_function_name=line.split()[1], nArgs_shift=5+int(line.split()[2])))
                    elif (line.split()[1] == "temp"):
                        result.append(push_pop_table[line.split()[0]][line.split()[1]].format(i=int(line.split()[2])+5))
                    elif (line.split()[1] == "pointer"):
                        result.append(push_pop_table[line.split()[0]][line.split()[1]].format(i=int(line.split()[2])+3))
                    else:
                        result.append(push_pop_table[line.split()[0]][line.split()[1]].format(i=line.split()[2], filename=filename.split(".")[0].split("/")[-1]))
                result.append("\n\n")
        return result

    res = [func_table["start"].format(filename=Path(sys.argv[1]).stem.split(".")[0])]
    if not os.path.isdir(sys.argv[1]):
        res = file_parse(sys.argv[1])
        with open(sys.argv[1].split(".")[0] + ".asm", "w") as file:
            for line in res:
                file.write(line)
        exit()
    elif len(glob.glob(sys.argv[1] + '/*.vm')) == 1:
        res = file_parse(glob.glob(sys.argv[1]  + '/*.vm')[0])
    else:
        for filename in glob.glob(sys.argv[1] + '/*.vm'):
            res += file_parse(filename)

    with open(sys.argv[1] + "/" + Path(sys.argv[1]).stem + ".asm", "w") as file:
        for line in res:
            file.write(line)
