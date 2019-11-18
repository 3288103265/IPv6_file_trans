import json
import os
import socket
import struct
import zlib

from tqdm import tqdm

sender = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
sender.connect(('::1', 8888))  # 与服务器建立连接
listener = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
listener.bind(('::1', 8887))
buffer = 1024

# 定制我们的报头，这里的报头不是唯一的，你可以根据你的想法去更改
head = {'filepath': r'D:\PythonFile\IPv6_file_trans',
        'filename': r'faces.zip',
        'filesize': None,
        'CRC32': None}

file_path = os.path.join(head['filepath'], head['filename'])

# 计算文件的大小
file_size = os.path.getsize(os.path.join(head['filepath'], head['filename']))
head['filesize'] = file_size

# 计算CRC32值并且和文件头里面的做比较。
with open(file_path, 'rb') as f:
    head['CRC32']=zlib.crc32(f.read())

json_head = json.dumps(head)  # 利用json将字典转成字符串
bytes_head = json_head.encode('utf-8')  # 字符串转bytes

# 计算head长度
head_len = len(bytes_head)  # 报头的长度
# 利用struct将int类型的数据打包成4个字节的byte，所以服务器端接受这个长度的时候可以固定缓冲区大小为4
pack_len = struct.pack('i', head_len)
# 先将报头长度发出去
sender.send(pack_len)
# 再发送bytes类型的报头
sender.send(bytes_head)

listener.listen()
conn, addr = listener.accept()
if_recv = conn.recv(1).decode('utf-8')
conn.close()
listener.close()

# 发送包的次数。每次发送一个buffer，剩下一个单独发送。
bags_num = file_size // buffer
if if_recv=='y':
    print('Sending...')
    with open(file_path, 'rb') as f:
        for i in tqdm(range(bags_num)):
            content = f.read(buffer)  # 每次读取buffer字节大小内容
            file_size -= buffer
            sender.send(content)  # 发送读取的内容
        if file_size > 0:
            content = f.read(file_size)
            sender.send(content)
            file_size = 0

else:
    print('Server reject your requrest.')

sender.close()
