import json
import socket

nodes = json.loads(open('nodes.json', 'r').read())
out = open('config', 'w+')

for key in nodes.keys():
	out.write('Host %s\n'%key.encode())
	out.write('\tHostName %s\n'%nodes.get(key).encode())
	out.write('\tUser cuhk_inc_01\n')
	out.write('\tIdentityFile ~/.ssh/planetlab2_rsa\n\n')
	print socket.gethostbyname(nodes.get(key).encode())
out.close()

out2 = open('nodes_addr.json', 'w+')
d = dict()
for key in nodes.keys():  # {"s1": "..."}
	hostname = nodes.get(key).encode()
	ip = socket.gethostbyname(hostname)
	d[key] = [ip, hostname]
	d[ip] = key
out2.write(json.dumps(d))
out2.close()
