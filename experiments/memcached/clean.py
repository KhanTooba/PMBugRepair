f = open("memcached_output.txt", "w")
for line in open("output.txt"):
    if "lru_maintainer_crawler_check" not in str(line):
        f.write(line)
f.close()