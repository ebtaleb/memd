#include <sys/types.h>
#include <sys/wait.h>
#include <stdio.h>
#include <sys/ptrace.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>

int main(int argc, const char *argv[])
{
    char mem_file_name[50];
    char buf[1024];
    pid_t pid = -1;
    int mem_fd = -1;
    off_t offset = 0;
    int page_size = getpagesize();

    if (argc != 2) {
        printf("Usage : %s [pid]\n", argv[0]);
        exit(1);
    }

    pid = atoi(argv[1]);
    printf("%d\n", pid);

    sprintf(mem_file_name, "/proc/%d/mem", pid);
    mem_fd = open(mem_file_name, O_RDONLY);
    ptrace(PT_ATTACH, pid, NULL, 0);
    waitpid(pid, NULL, 0);
    lseek(mem_fd, offset, SEEK_SET);
    read(mem_fd, buf, page_size);
    ptrace(PT_DETACH, pid, NULL, 0);

    printf("%s\n", buf);

    return 0;
}
