import cx_Freeze

executables = [cx_Freeze.Executable("main.py")]
# move all files to same directory
cx_Freeze.setup(
    name="Cactus Jump",
    options={"build_exe": {"packages": ["pygame"],
                           "include_files": ["hscore.txt", "platformer.py", "settings.py", "Setup.py",
                                             "Sprites.py", "boostsound.wav", "coinsound.wav",
                                             "deathsound.wav", "explsound.wav", "jump.wav", "Yeti.ogg",
                                             "bombsprite.png", "cactussprite.png", "spritesheet_jumper.png"]}},
    description="Cactus Game",
    executables=executables
)
