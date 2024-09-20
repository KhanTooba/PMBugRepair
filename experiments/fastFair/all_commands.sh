rm *.bc *.ll a.out
./commands.sh
./a.out
mv output.txt ../../results/outputs/fastFair_output.txt
rm *.bc *.ll a.out
