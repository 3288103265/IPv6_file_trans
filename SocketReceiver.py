import socket
import struct
import json
import zlib

from tqdm import tqdm

server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
server.bind(('::1', 8888))  # 绑定ip地址和端口
server.listen()  # 开启监听
print('Listening...')
buffer = 1024  # 缓冲区大小
conn, addr = server.accept()

# 先接收报头的长度
head_len = conn.recv(4)
head_len = struct.unpack('i', head_len)[0]  # 将报头长度解包出来
# 再接收报头
json_head = conn.recv(head_len).decode('utf-8')  # 拿到的是bytes类型的数据，要进行转码
head = json.loads(json_head)  # 拿到原本的报头
file_name = head['filename']
file_size = head['filesize']
src_crc32 = head['CRC32']

# 回复拒绝或者接受
server2 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
server2.connect(('::1', 8887))
print("A request try to send you of a file: accept or not[y/n]? ")
print("Requset IP:'{}'".format(addr[0]))
print("Filename:{}".format(file_name))
print("Filesize:{} bytes".format(file_size))
if_recv = input("Accept or not [y/n]?\n")
assert (if_recv=='y' or if_recv=='n')
server2.send(if_recv.encode('utf-8'))

# 发送速度要求
speed = input('Speed(kb/s):\n')
server2.send(speed.encode('utf-8'))
server2.close()

bags_nums = file_size//buffer
if not if_recv=='n':
    with open('recv.zip', 'wb') as f:
        for i in tqdm(range(bags_nums), ncols=100, desc="Receiving", unit='kb'):
            content = conn.recv(buffer)
            f.write(content)
            file_size -= buffer
        if file_size > 0:
            content = conn.recv(file_size)
            f.write(content)
            file_size = 0

    with open('recv.zip', 'rb') as f:
        dst_crc32 = zlib.crc32(f.read())
    if dst_crc32==src_crc32:
        print('Receive {} successfully.'.format(file_name))
    else:
        print('File received invalid.')
conn.close()
server.close()
