g++ array.cpp -I ../ -I../../include -lpmemobj -lpmem

sudo rm /mnt/pmfs/pool2
sudo ./a.out /mnt/pmfs/pool2 alloc arr 10

sudo ./a.out /mnt/pmfs/pool2 print arr
