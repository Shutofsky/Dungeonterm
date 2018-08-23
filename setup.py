from cx_Freeze import setup, Executable

setup(
    name = "DungeonTerm",
    version = "0.3",
    description = "Stalkert Tula",
    executables = [Executable("f3term.py")]
)