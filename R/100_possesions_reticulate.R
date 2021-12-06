library(reticulate)
reticulate::use_python(python = "env/bin/python3.9")

reticulate::source_python(file = "src/per_100_possessions.py")