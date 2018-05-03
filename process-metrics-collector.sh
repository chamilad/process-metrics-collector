#!/bin/bash

# process id to monitor
pid=$1

if [ -z $1 ]; then
  echo "ERROR: Process ID not specified."
  echo
  echo "Usage: $(basename "$0") <PID>"
  exit 1
fi

# check if process exists
kill -0 $pid > /dev/null 2>&1
pid_exist=$?

if [ $pid_exist != 0 ]; then
  echo "ERROR: Process ID $pid not found."
  exit 1
fi

current_time=$(date +"%Y_%m_%d_%H%M")
dir_name="data/${pid}-${current_time}"
csv_filename="${dir_name}/metrics.csv"

# create data directory
mkdir -p $dir_name




# Read collected metrices from the CSV file and plot graphs
#
# This function will end script execution.
#
# This function is to be called after an interrupt like SIGINT or SIGKILL
# is received.
#
function plotGraph() {

  # bring cursor to next line after interrupt
  echo

  # plot graphs if there is a data file
  if [ -f $csv_filename ]; then
    echo "Plotting graphs..."
    gnuplot <<- EOF
      # Output to png with a font size of 10, using pngcairo for anti-aliasing
      set term pngcairo size 1024,800 noenhanced font "Helvetica,10"

      # Set border color around the graph
      set border ls 50 lt rgb "#939393"

      # Hide left and right vertical borders
      set border 16 lw 0
      set border 64 lw 0

      # Set tic color
      set tics nomirror textcolor rgb "#939393"

      # Set horizontal lines on the ytics
      set grid ytics lt 1 lc rgb "#d8d8d8" lw 2

      # Rotate x axis lables
      set xtics rotate

      # Set graph size relative to the canvas
      set size 1,0.85

      # Set separator to comma
      set datafile separator ","

      # Move legend to the bottom
      set key bmargin center box lt rgb "#d8d8d8" horizontal

      # Plot graph,
      # xticlabels(1) - first column as x tic labels
      # "with lines" - line graph
      # "smooth unique"
      # "lw 2" - line width
      # "lt rgb " - line style color
      # "t " - legend labels
      #
      # CPU and memory usage
      set output "${dir_name}/cpu-mem-usage.png"
      set title "CPU and Memory Usage for Proces ID $pid"
      plot "$csv_filename" using 2:xticlabels(1) with lines smooth unique lw 2 lt rgb "#4848d6" t "CPU Usage %",\
       "$csv_filename" using 3:xticlabels(1) with lines smooth unique lw 2 lt rgb "#b40000" t "Memory Usage %"

      # TCP count
      set output "${dir_name}/tcp-count.png"
      set title "TCP Connections Count for Proces ID $pid"
      plot "$csv_filename" using 4:xticlabels(1) with lines smooth unique lw 2 lt rgb "#ed8004" t "TCP Connection Count"

      # Thread count
      set output "${dir_name}/thread-count.png"
      set title "Thread Count for Proces ID $pid"
      plot "$csv_filename" using 5:xticlabels(1) with lines smooth unique lw 2 lt rgb "#48d65b" t "Thread Count"

       # All together
       set output "${dir_name}/all-metrices.png"
       set title "All Metrics for Proces ID $pid"
       plot "$csv_filename" using 2:xticlabels(1) with lines smooth unique lw 2 lt rgb "#4848d6" t "CPU Usage %",\
        "$csv_filename" using 3:xticlabels(1) with lines smooth unique lw 2 lt rgb "#b40000" t "Memory Usage %", \
        "$csv_filename" using 4:xticlabels(1) with lines smooth unique lw 2 lt rgb "#ed8004" t "TCP Connection Count", \
        "$csv_filename" using 5:xticlabels(1) with lines smooth unique lw 2 lt rgb "#48d65b" t "Thread Count"
EOF
  fi

  echo "Done!"
  exit 0
}

# add SIGINT & SIGTERM trap
trap "plotGraph" SIGINT SIGTERM SIGKILL



echo "Writing data to CSV file $csv_filename..."
touch $csv_filename

# write CSV headers
echo "Time,CPU,Memory,TCP Connections,Thread Count" >> $csv_filename

# check if process exists
kill -0 $pid > /dev/null 2>&1
pid_exist=$?

# collect until process exits
while [ $pid_exist == 0 ]; do
  # check if process exists
  kill -0 $pid > /dev/null 2>&1
  pid_exist=$?

  if [ $pid_exist == 0 ]; then
    # read cpu and mem percentages
    timestamp=$(date +"%b %d %H:%M:%S")
    cpu_mem_usage=$(top -b -n 1 | grep -w -E "^ *$pid" | awk '{print $9 "," $10}')
    tcp_cons=$(lsof -i -a -p $pid -w | tail -n +2 | wc -l)
    tcount=$(ps -o nlwp h $pid | tr -d ' ')

    # write CSV row
    echo "$timestamp,$cpu_mem_usage,$tcp_cons,$tcount" >> $csv_filename
    sleep 5
  fi
done

# draw graph
plotGraph
