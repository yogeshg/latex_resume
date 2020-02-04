import argh

section_format = """
\input{default}
"""


def get_markdown(section, output):
    with open(section, 'r') as in_file:
        with open(output, 'w') as out_file:
            text = section_format
            out_file.write(text)



if __name__ == "__main__":
    p = argh.ArghParser()
    p.add_commands([get_markdown])
    p.dispatch()

