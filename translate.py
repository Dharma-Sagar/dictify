


if __name__ == '__main__':
    for f in Path('input').glob('*.txt'):


        file_name, extension = os.path.splitext(f.name)
        out_f_es = Path('output') / os.path.normpath(file_name+"es.po")
        out_f_pt = Path('output') / os.path.normpath(file_name+"pt.po")

        write_tuple_to_file(out_f_es,out,"es")
        write_tuple_to_file(out_f_pt, out,"pt")