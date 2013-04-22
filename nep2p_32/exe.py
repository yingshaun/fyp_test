from bbfreeze import Freezer

f = Freezer("build")
f.addScript("run.py")
f.addScript("cli.py")
f()
