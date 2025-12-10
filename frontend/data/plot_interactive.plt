# ==========================================
# KONFIGURASI GRAFIK INTERAKTIF (POP-UP)
# ==========================================

# Judul dan Label
set title "Memonitor Data Sensor (Mode Interaktif)" font "Segoe UI,14"
set datafile separator ","
set xlabel "Waktu (Detik)"
set ylabel "Nilai Sensor (PPM)"

# Grid dan Legenda
set grid xtics ytics mytics
set key outside right center box title "Legenda"
set style data lines

# Definisi Warna (Sama dengan versi PNG)
set style line 1 lc rgb '#FF9AA2' lw 2 pt 7 ps 0.5
set style line 2 lc rgb '#B5EAD7' lw 2 pt 7 ps 0.5
set style line 3 lc rgb '#C7CEEA' lw 2 pt 7 ps 0.5
set style line 4 lc rgb '#FFDAC1' lw 2 pt 7 ps 0.5
set style line 5 lc rgb '#E2F0CB' lw 2 pt 7 ps 0.5
set style line 6 lc rgb '#FFB7B2' lw 2 pt 7 ps 0.5
set style line 7 lc rgb '#E0BBE4' lw 2 pt 7 ps 0.5

# Plotting Data (ARG1 = Nama File CSV)
plot ARG1 using 1:2 every ::6 ls 1 title "GM-NO2", \
     ARG1 using 1:3 every ::6 ls 2 title "GM-Ethanol", \
     ARG1 using 1:4 every ::6 ls 3 title "GM-VOC", \
     ARG1 using 1:5 every ::6 ls 4 title "GM-CO", \
     ARG1 using 1:6 every ::6 ls 5 title "MiCS-CO", \
     ARG1 using 1:7 every ::6 ls 6 title "MiCS-Ethanol", \
     ARG1 using 1:8 every ::6 ls 7 title "MiCS-VOC"

# Tahan window agar tidak langsung tertutup
pause mouse close