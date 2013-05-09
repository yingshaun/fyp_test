import json

nodes = json.loads(open('ssh_config.json', 'r').read())
out = open('config', 'w+')

for key in nodes.keys():
	out.write('Host %s\n'%key.encode())
	out.write('\tHostName %s\n'%nodes.get(key).encode())
	out.write('\tUser cuhk_inc_01\n')
	out.write('\tIdentityFile ~/.ssh/planetlab2_rsa\n\n')

