name=system("ls *.gen | tail -1")
plot name using (column(-1)):2 t name
