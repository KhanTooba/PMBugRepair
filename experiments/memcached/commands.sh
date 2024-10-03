#rm output.txt
cd src
sudo sh commands.sh
cd ..
sudo rm src/output.txt && ./memcachedMulti
cp src/output.txt ./
mv output.txt ../../results/outputs/memcached_output.txt
