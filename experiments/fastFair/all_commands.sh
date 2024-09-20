rm output.txt cleanOutput.txt
rm *.bc *.ll a.out
./commands.sh
./a.out

python3 cleanTrace.py output.txt cleanOutput.txt

mv cleanOutput.txt ../../results/outputs/fastFair_output.txt
rm *.bc *.ll a.out
