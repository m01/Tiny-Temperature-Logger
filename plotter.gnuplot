set xdata time
set timefmt "%d.%m.%Y-%H:%M"
set xlabel "Time"
set ylabel "Temperature (°C)"
set title "My temperature chart"
set size 0.7,0.7
plot "temp_25.05.2011.log" using 1:2 title 'Temp' with lines
