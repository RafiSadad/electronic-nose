# Konfigurasi Output
set term pngcairo size 1000,600 font "Segoe UI,10" background "#FFFFFF"
set output ARG2  # Parameter 2: Nama file output (.png)

# Konfigurasi Grafik
set title "Hasil Analisis GNUPLOT: Respon Sensor" font "Segoe UI,14"
set datafile separator ","
set xlabel "Waktu (Detik)"
set ylabel "Nilai Sensor (V)"
set grid xtics ytics mytics
set key outside right center box title "Legenda"

# Definisi Style Garis (Warna Pastel yang kamu pakai)
set style line 1 lc rgb '#FF9AA2' lw 2 pt 7 ps 0.5
set style line 2 lc rgb '#B5EAD7' lw 2 pt 7 ps 0.5
set style line 3 lc rgb '#C7CEEA' lw 2 pt 7 ps 0.5
set style line 4 lc rgb '#FFDAC1' lw 2 pt 7 ps 0.5
set style line 5 lc rgb '#E2F0CB' lw 2 pt 7 ps 0.5
set style line 6 lc rgb '#FFB7B2' lw 2 pt 7 ps 0.5
set style line 7 lc rgb '#E0BBE4' lw 2 pt 7 ps 0.5

# Perintah Plotting
# ARG1 = Parameter 1 (Nama file CSV)
# every ::6 = Skip 6 baris pertama (Metadata + Header), mulai baca baris 7
plot ARG1 using 1:2 every ::6 with lines ls 1 title "GM-NO2", \
     ARG1 using 1:3 every ::6 with lines ls 2 title "GM-Ethanol", \
     ARG1 using 1:4 every ::6 with lines ls 3 title "GM-VOC", \
     ARG1 using 1:5 every ::6 with lines ls 4 title "GM-CO", \
     ARG1 using 1:6 every ::6 with lines ls 5 title "MiCS-CO", \
     ARG1 using 1:7 every ::6 with lines ls 6 title "MiCS-Ethanol", \
     ARG1 using 1:8 every ::6 with lines ls 7 title "MiCS-VOC"