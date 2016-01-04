#! /usr/bin/env python3
import ctypes, re, sys, io
import pdb

# Adapted for FreeBSD

## Partial interface to ptrace(2), only for PT_ATTACH and PT_DETACH.
c_ptrace = ctypes.CDLL("libc.so.7").ptrace
c_pid_t = ctypes.c_int32 # This assumes pid_t is int32_t
c_caddr_t = ctypes.c_char_p
c_ptrace.argtypes = [ctypes.c_int, c_pid_t, ctypes.c_char_p, ctypes.c_int]

def ptrace(attach, pid):
    op = ctypes.c_int(10 if attach else 11) #PT_ATTACH or PT_DETACH
    c_pid = c_pid_t(pid)
    null = c_caddr_t(0)
    data = ctypes.c_int(0)
    err = c_ptrace(op, c_pid, null, data)
    if err != 0: raise Exception('ptrace', err)

## Parse a line in /proc/$pid/map. Return the boundaries of the chunk
## the read permission character.
def maps_line_range(line):
    m = re.match(r'(0x[0-9A-Fa-f]+) (0x[0-9A-Fa-f]+) ([0-9]+) ([0-9]+) (0x[0-9A-Fa-f]+|0) ([-r])', line)
    # m = re.match(r'([0-9A-Fa-f]+) ([0-9A-Fa-f]+) ([0-9]+) ([0-9]+) ([0-9A-Fa-f]+) ([-r])', line)
    return [int(m.group(1)[2:], 16), int(m.group(2)[2:], 16), m.group(6)]

## Dump the readable chunks of memory mapped by a process
def cat_proc_mem(pid):
    ## Apparently we need to ptrace(PT_ATTACH, $pid) to read /proc/$pid/mem
    try:

        pdb.set_trace()
        ptrace(True, int(pid))
        ## Read the memory maps to see what address ranges are readable
        maps_file = io.open("/proc/" + pid + "/map", 'r')
        ranges = map(maps_line_range, maps_file.readlines())
        ## Read the readable mapped ranges
        mem_file = io.open("/proc/" + pid + "/mem", 'rb', buffering=0)
        for r in ranges:
            if r[2] == 'r':
                mem_file.seek(r[0])
                chunk = mem_file.read(r[1] - r[0])
                print(chunk)
    except:
        print("faileure")
    ## Cleanup
    finally:
        maps_file.close()
        mem_file.close()
        ptrace(False, int(pid))

if __name__ == "__main__":
    for pid in sys.argv[1:]:
        cat_proc_mem(pid)
