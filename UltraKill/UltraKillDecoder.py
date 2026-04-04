"""
UltraKillDecoder.py
Author: Aztharot
Github: https://github.com/Aztharot-RO0t3d
Date: 2026/04/03

Description:
Decodificador y editor de archivos .Bepis para ultrakill
"""

import struct
import sys
import re
from pathlib import Path
from typing import IO
from rich.console import Console

console = Console()

output_file = None
captured_lines = []
indent = 0

type_names = [
    "bool","byte","char","???","decimal","double","i16","i32","i64","i8",
    "single","time_span","date_time","u16","u32","u64","null","string",
]

prim_readers = [
    lambda x: bool(x.read(1)[0]),
    lambda x: x.read(1)[0],
    lambda x: chr(x.read(1)[0]),
    None,
    lambda x: _read_str(x),
    lambda x: struct.unpack("<d", x.read(8))[0],
    lambda x: struct.unpack("<h", x.read(2))[0],
    lambda x: struct.unpack("<i", x.read(4))[0],
    lambda x: struct.unpack("<l", x.read(8))[0],
    lambda x: struct.unpack("<b", x.read(1))[0],
    lambda x: struct.unpack("<f", x.read(4))[0],
    lambda x: struct.unpack("<l", x.read(8))[0],
    lambda x: (x.read(8), 0)[1],
    lambda x: struct.unpack("<H", x.read(2))[0],
    lambda x: struct.unpack("<I", x.read(4))[0],
    lambda x: struct.unpack("<L", x.read(8))[0],
    lambda x: None,
    lambda x: _read_str(x),
]

bin_type_enums = [
    "Primitive","String","Object","SystemClass",
    "Class","Object[]","String[]","Primitive[]",
]


def _pos_of(i: IO, offset: int = 0):
    return hex(i.tell() + offset)


def _read_str(i: IO):
    ln = i.read(1)
    if not ln:
        return ""
    ln = ln[0]
    data = i.read(ln)
    return data.decode("utf8", errors="ignore")


def fancy_print(t):
    global output_file, captured_lines
    line = "  " * indent + t

    console.print(line)

    clean = re.sub(r"\[.*?\]", "", line)
    captured_lines.append(clean)

    if output_file:
        output_file.write(clean + "\n")


def print_prop(a, b):
    fancy_print(f"{a} = {b}")


def ind():
    global indent
    indent += 1


def ded():
    global indent
    indent -= 1


class indented:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        global indent
        fancy_print(self.name + " {")
        indent += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        global indent
        indent -= 1
        fancy_print("}")


def _decode_ser_header_record(i: IO):
    root_id = struct.unpack("<i", i.read(4))[0]
    header_id = struct.unpack("<i", i.read(4))[0]
    maj_ver = struct.unpack("<i", i.read(4))[0]
    min_ver = struct.unpack("<i", i.read(4))[0]

    with indented("SerializedStreamHeader"):
        print_prop("root_id", root_id)
        print_prop("header_id", header_id)
        print_prop("major_ver", maj_ver)
        print_prop("minor_ver", min_ver)


def _decode_class_with_id(i: IO):
    obj_id = struct.unpack("<i", i.read(4))[0]
    metadata_id = struct.unpack("<i", i.read(4))[0]

    with indented("ClassWithId"):
        print_prop("object_id", obj_id)
        print_prop("metadata_id", metadata_id)


class ClassInfo:
    def __init__(self, i: IO):
        self.io = i
        self.name = ""
        self.members = []

    def populate(self):
        self.io.read(4)
        self.name = _read_str(self.io)
        m_cnt = struct.unpack("<i", self.io.read(4))[0]

        for _ in range(m_cnt):
            self.members.append(_read_str(self.io))


class MemberTypeInfo:
    def __init__(self, i: IO, member_count: int):
        self.io = i
        self.member_count = member_count
        self.bin_type_enums = []
        self.additional_infos = []

    def populate(self):
        r = self.io.read(self.member_count)

        for x in r:
            if x == 0 or x == 7:
                self.additional_infos += self.io.read(1)
            elif x == 3:
                self.additional_infos.append(_read_str(self.io))
            elif x == 4:
                _read_str(self.io)
                self.io.read(4)
                self.additional_infos.append(None)
            else:
                self.additional_infos.append(None)

        self.bin_type_enums = list(r)


def _decode_cls_with_members_and_types(i: IO):
    cls_info = ClassInfo(i)
    cls_info.populate()

    member_type_info = MemberTypeInfo(i, len(cls_info.members))
    member_type_info.populate()

    lib_id = struct.unpack("<i", i.read(4))[0]
    values = []

    for (x, info) in zip(
        member_type_info.bin_type_enums,
        member_type_info.additional_infos
    ):
        if x == 0:
            pos = i.tell()
            try:
                val = prim_readers[info - 1](i)
            except:
                val = "ERR"
            values.append((val, pos))
        else:
            values.append(("?", i.tell()))

    with indented("ClassWithMembersAndTypes"):
        print_prop("name", cls_info.name)

        fancy_print("fields = [")
        ind()

        for name, value in zip(cls_info.members, values):
            fancy_print(f"{name} = {value[0]} @ {hex(value[1])}")

        ded()
        fancy_print("]")

        print_prop("library_id", lib_id)


def _decode_binary_library(i: IO):
    lib_id = struct.unpack("<i", i.read(4))[0]
    lib_name = _read_str(i)

    with indented("BinaryLibrary"):
        print_prop("library_id", lib_id)
        print_prop("library_name", lib_name)


def _decode_prim_array(i: IO):
    oid = struct.unpack("<i", i.read(4))[0]
    length = struct.unpack("<i", i.read(4))[0]
    tpe = i.read(1)[0]

    reader = prim_readers[tpe - 1]
    els = []

    for _ in range(length):
        try:
            els.append(reader(i))
        except:
            els.append("ERR")

    with indented("PrimitiveArray"):
        print_prop("id", oid)
        print_prop("length", length)
        fancy_print(f"elements = {els}")


deserializers = {
    0: _decode_ser_header_record,
    1: _decode_class_with_id,
    5: _decode_cls_with_members_and_types,
    12: _decode_binary_library,
    15: _decode_prim_array,
    11: lambda i: fancy_print("-- End --"),
}


def decode(i: IO):
    while True:
        try:
            buf = i.read(1)
            if len(buf) == 0:
                break

            current_id = buf[0]

            if current_id not in deserializers:
                break

            deserializers[current_id](i)

        except Exception as e:
            fancy_print(f"[ERROR] {e}")
            break

def interactive_edit(bepis_path):
    global captured_lines

    with open(bepis_path, "r+b") as f:
        i = 0

        while i < len(captured_lines):
            print("\n===== BLOQUE =====")

            block = captured_lines[i:i+5]

            for idx, line in enumerate(block):
                print(f"{idx}: {line}")

            print("\nOpciones:")
            print("n = siguiente")
            print("p = anterior")
            print("q = salir")
            print("0-4 = editar")

            choice = input(">> ").strip()

            if choice == "n":
                i += 5
                continue
            elif choice == "p":
                i = max(0, i - 5)
                continue
            elif choice == "q":
                break
            elif choice.isdigit():
                idx = int(choice)

                if 0 <= idx < len(block):
                    line = block[idx]

                    match = re.search(r"(\w+) = ([\w\d]+).*?(0x[0-9a-fA-F]+)", line)

                    if not match:
                        print("[!] No editable")
                        continue

                    name, old_value, offset = match.groups()
                    offset = int(offset, 16)

                    print(f"Editar {name} (actual {old_value})")
                    new_val = input("Nuevo valor: ")

                    try:
                        if old_value in ["True", "False"]:
                            val = new_val.lower() == "true"
                            f.seek(offset)
                            f.write(b"\x01" if val else b"\x00")
                        else:
                            val = int(new_val)
                            f.seek(offset)
                            f.write(struct.pack("<i", val))

                        print(f"[+] {name} modificado")
                    except:
                        print("[!] Error al escribir")

                else:
                    print("[!] Índice inválido")
            else:
                print("[!] Opción inválida")


def main():
    global output_file

    if len(sys.argv) < 2:
        print("syntax: script.py file.bepis")
        sys.exit(1)

    f = Path(sys.argv[1])

    if not f.is_file():
        print(f"! {f} no existe")
        sys.exit(1)

    txt_name = f.with_suffix(".txt")

    with open(f, "rb") as file, open(txt_name, "w", encoding="utf-8") as output_file:
        decode(file)

    print(f"[+] Output guardado en: {txt_name}")

    interactive_edit(f)


if __name__ == "__main__":
    main()