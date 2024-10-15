clang++-10 queue.cpp -I ../ -I../../include -lpmemobj -lpmem

sudo rm /mnt/pmfs/pool3
sudo ./a.out /mnt/pmfs/pool3 push 1
sudo ./a.out /mnt/pmfs/pool3 push 2
sudo ./a.out /mnt/pmfs/pool3 push 3
sudo ./a.out /mnt/pmfs/pool3 show
sudo ./a.out /mnt/pmfs/pool3 pop
sudo ./a.out /mnt/pmfs/pool3 show

