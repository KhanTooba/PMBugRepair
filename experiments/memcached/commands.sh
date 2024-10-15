
#rm output.txt
#cd src
#sudo sh commands.sh
#cd ..
sudo rm src/output.txt && ./client
cp src/output.txt ./
mv output.txt ../../results/outputs/memcached_output.txt
