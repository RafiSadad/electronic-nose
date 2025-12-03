# Konfigurasi Output (Window Interaktif)
set term wxt size 1200,800 persist font "Segoe UI,10"
set title "Respon Sinyal Electronic Nose (7 Sensor)" font "Segoe UI,14"

# Konfigurasi Sumbu
set datafile separator ","
set xlabel "Waktu (Detik)"
set ylabel "Nilai Sensor (V / ppm)"
set grid
set key outside right center box

# Dekorasi Garis (Warna Pastel sesuai App Python Anda)
set style line 1 lc rgb '#FF9AA2' lw 2 pt 7 ps 0.5 # Sensor 1
set style line 2 lc rgb '#B5EAD7' lw 2 pt 7 ps 0.5 # Sensor 2
set style line 3 lc rgb '#C7CEEA' lw 2 pt 7 ps 0.5 # Sensor 3
set style line 4 lc rgb '#FFDAC1' lw 2 pt 7 ps 0.5 # Sensor 4
set style line 5 lc rgb '#E2F0CB' lw 2 pt 7 ps 0.5 # Sensor 5
set style line 6 lc rgb '#FFB7B2' lw 2 pt 7 ps 0.5 # Sensor 6
set style line 7 lc rgb '#E0BBE4' lw 2 pt 7 ps 0.5 # Sensor 7

# Baca Filename dari argumen command line
# ARG1 adalah nama file CSV yang akan dipassing nanti
DATAFILE = ARG1

# Plotting
# skip 6 digunakan untuk melewati metadata di file CSV Anda
plot DATAFILE using 1:2 every ::6 with lines ls 1 title "GM-NO2", \
     DATAFILE using 1:3 every ::6 with lines ls 2 title "GM-Ethanol", \
     DATAFILE using 1:4 every ::6 with lines ls 3 title "GM-VOC", \
     DATAFILE using 1:5 every ::6 with lines ls 4 title "GM-CO", \
     DATAFILE using 1:6 every ::6 with lines ls 5 title "MiCS-CO", \
     DATAFILE using 1:7 every ::6 with lines ls 6 title "MiCS-Ethanol", \
     DATAFILE using 1:8 every ::6 with lines ls 7 title "MiCS-VOC"