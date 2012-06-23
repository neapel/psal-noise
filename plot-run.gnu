name=system("ls output/*.pop | tail -1")
plot name using (1 + column(-1) + 0.5 * (rand(0) - 0.5)):2 w p pt 5 ps 0.1 t name
