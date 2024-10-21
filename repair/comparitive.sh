mv Report.txt Report_original.txt
touch ComparitiveResults.txt

for i in $(seq 2 2 65); do
    input_file="../experiments/fastFair/comparitive/fastFair_$i.txt"
    
    if [ -f "$input_file" ]; then
        python3 trace_formatter.py "$input_file" tempFastFair.txt
        
        t1=$(date +%s.%N)
        python3 step1.py tempFastFair.txt tempFastFair1.txt fastFair
        t2=$(date +%s.%N)
        
        python3 step4.py tempFastFair1.txt tempFastFair2.txt fastFair
        t3=$(date +%s.%N)

        execution_time_1=$(echo "$t2 - $t1" | bc)
        execution_time_2=$(echo "$t3 - $t2" | bc)

        echo "$i, $execution_time_1, $execution_time_2" >> ComparitiveResults.txt
        rm tempFastFair.txt tempFastFair1.txt tempFastFair2.txt temp_results.txt
    else
        echo "File $input_file does not exist." >> ComparitiveResults.txt
    fi
done


mv Report.txt Report_comparitiveAnalysis.txt
mv ComparitiveResults.txt ../experiments/ComparitiveResults.txt