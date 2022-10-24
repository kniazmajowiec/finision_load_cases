import sys
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename


def ask_for_input_files():
    """ Popping up window for user to input files and parameters for the script """
    def close_window():
        tk.Tk().destroy()
        window.destroy()

    def ask_path(file_path, file_tuple):
        f_path = askopenfilename(filetypes=file_tuple)
        file_path.set(f_path)

    def ask_dir(_dir):
        dir_path = askdirectory()
        _dir.set(dir_path)

    window = tk.Tk()
    window.title('Upload input files')
    window.geometry('1200x400')

    xml_gd, xml_if,  = tk.StringVar(), tk.StringVar(),

    file_paths = [xml_gd, xml_if]

    lbl1 = tk.Label(window, text="Choose xml with data from SCIA (Members, Loads, Load cases)")
    lbl1.grid(column=0, row=1, sticky="W", padx=20)
    txt1 = tk.Entry(window, width=120, textvariable=xml_gd)
    txt1.grid(column=1, row=1)
    button1 = tk.Button(window, text="Find path",
                        command=lambda: ask_path(xml_gd, [("SCIA xml", '.xml')]))
    button1.grid(column=2, row=1, sticky="W")

    lbl2 = tk.Label(window, text="Choose xl with loads to change")
    lbl2.grid(column=0, row=2, sticky="W", padx=20)
    txt2 = tk.Entry(window, width=120, textvariable=xml_if)
    txt2.grid(column=1, row=2)
    button2 = tk.Button(window, text="Find path",
                        command=lambda: ask_path(xml_if, [("excel file", '.xlsx')]))
    button2.grid(column=2, row=2, sticky="W")

    # lbl3 = tk.Label(window, text="Choose excel file with min reinforcement data")
    # lbl3.grid(column=0, row=4, sticky="W", padx=20)
    # txt3 = tk.Entry(window, width=120, textvariable=xl_)
    # txt3.grid(column=1, row=4)
    # button3 = tk.Button(window, text="Find path", command=lambda: ask_path(xl_, [("excel file", '.xlsx')]))
    # button3.grid(column=2, row=4, sticky="W")
    #
    # lbl3i5 = tk.Label(window, text="Choose excel file with predefined reinforcement\n(optional, so far no opti)")
    # lbl3i5.grid(column=0, row=5, sticky="W", padx=20)
    # txt3i5 = tk.Entry(window, width=120, textvariable=xl_ext)
    # txt3i5.grid(column=1, row=5)
    # button3o5 = tk.Button(window, text="Find path", command=lambda: ask_path(xl_ext, [("excel file", '.xlsx')]))
    # button3o5.grid(column=2, row=5, sticky="W")
    #
    # lbl4 = tk.Label(window, text="Choose directory to store results")
    # lbl4.grid(column=0, row=6, sticky="W", padx=20)
    # txt4 = tk.Entry(window, width=120, textvariable=output_directory)
    # txt4.grid(column=1, row=6)
    # button3 = tk.Button(window, text="Find path", command=lambda: ask_dir(output_directory))
    # button3.grid(column=2, row=6, sticky="W")
    #
    # lbl5 = tk.Label(window, text='Faster calculation')  # what kind of factor to take in opti if True then UC else 1.01
    # lbl5.grid(column=0, row=7, sticky="W", padx=20)
    # chb = tk.Checkbutton(window, var=rough_bool)
    # chb.grid(column=1, row=7, sticky="W", padx=20)
    #
    # lbl6 = tk.Label(window, text="Rebars diameters (separated by ;)")
    # lbl6.grid(column=0, row=8, sticky="W", padx=20)
    # txt6 = tk.Entry(window, width=60, textvariable=rebars)
    # txt6.grid(column=1, row=8, sticky="W", padx=20)
    #
    # lbl7 = tk.Label(window, text="Stirrups diameters (separated by ;)")
    # lbl7.grid(column=0, row=9, sticky="W", padx=20)
    # txt7 = tk.Entry(window, width=60, textvariable=stirrups)
    # txt7.grid(column=1, row=9, sticky="W", padx=20)
    #
    # lbl8 = tk.Label(window, text="Stirrups spacing (separated by ;)")
    # lbl8.grid(column=0, row=10, sticky="W", padx=20)
    # txt8 = tk.Entry(window, width=60, textvariable=spacing)
    # txt8.grid(column=1, row=10, sticky="W", padx=20)
    #
    # lbl9 = tk.Label(window, text="Max reinforcement [%]")
    # lbl9.grid(column=0, row=11, sticky="W", padx=20)
    # txt9 = tk.Entry(window, width=60, textvariable=four_per_cent)
    # txt9.grid(column=1, row=11, sticky="W", padx=20)
    #
    # lbl10 = tk.Label(window, text="lambda - factor of effective length")
    # lbl10.grid(column=0, row=12, sticky="W", padx=20)
    # txt10 = tk.Entry(window, width=60, textvariable=_lambda)
    # txt10.grid(column=1, row=12, sticky="W", padx=20)

    button = tk.Button(window, text="Save and next", command=close_window, height=1, width=15)
    button.grid(column=0, row=13, sticky="W", padx=20)

    window.mainloop()
    return [f.get() for f in file_paths]


def progressbar(it, prefix="", size: int = 60):
    """ Print a progress bar with:
        it - enumerable of objects
        prefix - Name shown on the progress bar
        size - length of the progress bar in characters """
    count = len(it)

    def show(j):
        try:
            x = int(size*j/count)
        except ZeroDivisionError:
            x = 0
        _text = f"{prefix}[{u'█'*x}{'.'*(size-x)}] {j}/{count}\r"
        print(_text, end='')

    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)


def show_exception_and_exit(exc_type, exc_value, tb):
    """Shows the exception and does not close the window"""
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)

if __name__ == '__main__':
    pass
