import json

nodes = json.loads(open('ssh_config.json', 'r').read())
out = open('config', 'w+')

for key in nodes.keys():
	out.write('Host %s\n'%key.encode())
	out.write('\tHostName %s\n'%nodes.get(key).encode())
	out.write('\tUser cuhk_inc_01\n')
	out.write('\tIdentityFile ~/.ssh/planetlab2_rsa\n\n')
out.close()

out2 = open('resolver', 'w+')
d = dict()
out2.write('{')
for key in nodes.keys():
	out2.write('"%s": {\n'%key)
	out2.write('\t"host": "cuhk_inc_01@%s",\n'%nodes[key])
	out2.write('\t"type": "key",\n')
	out2.write('\t"key": "PlanetLabKey",\n')
	out2.write('},\n')
out2.write('}')
