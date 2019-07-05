from telethon.sync import TelegramClient
import os.path
import json
import re
from urlextract import URLExtract
from urllib.parse import urlparse


def processchats(chat):

	extractor = URLExtract()

	print("processing " + chat)

	chat = chat.lower()
	jsonfn = "./jsons/"+chat+".json"

	if chat not in nodes:
		nodes[chat] = {}
		nodes[chat]["name"] = chat
		nodes[chat]["done"] = False
		nodes[chat]["type"] = ""
		nodes[chat]["is_channel"] = False

	if maxdepth == 0:
		nodes[chat]["type"] = "seed"

	if os.path.isfile(jsonfn):
		print(jsonfn + " found")
		with open(jsonfn, 'r') as f:
			messagelist = json.load(f)

	else:

		messagelist = []

		with TelegramClient(name, api_id, api_hash) as client:

			#taking out the entituy check since the get_entity method requires a lot of API tokens
			try:
				ch = client.get_entity(chat)
			except:
				print(chat + " is not a telegram entity")
				#quit()
				return


			if type(ch).__name__ != "Channel":
				print(chat + " is not a channel")
				return



			for msg in client.iter_messages(chat):

				print(msg.sender_id, ':', msg.text)
				
				newmsg = {}
				newmsg["sender_id"] = msg.sender_id
				newmsg["chat"] = chat
				newmsg["text"] = msg.text
				newmsg["date"] = msg.date.strftime("%Y-%m-%d %H:%M:%S")
				newmsg["views"] = msg.views

				messagelist.append(newmsg)

				if get_images is not False:
					if msg.media is not None:
						client.download_media(msg.media, folder)
					#break

		with open(jsonfn, "w") as outfile:
			json.dump(messagelist, outfile)

		#quit()

	mentions = {}
	domains = {}
	for msg in messagelist:

		if type(msg["text"]) == str:
		
			# extract @mentions (possibly other channels)
			mysearch = re.search(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)',msg["text"])

			if mysearch is not None:
				id = mysearch.group(0)

				id = id[1:].lower()
				
				if id not in mentions:
					mentions[id] = 0

				mentions[id] += 1

			# extract URLs/domain names
			urls = extractor.find_urls(msg["text"])
			for url in urls:

				parsed_uri = urlparse(url)
				domain = parsed_uri.netloc.replace("www.","")

				if domain == "":
					continue

				domain = domain.lower()

				if domain not in domains:
					domains[domain] = 0
				domains[domain] += 1

	#print(mentions)
	#quit()

	for mention in mentions:

		#themention = mention[1:].lower()
		

		if mention not in nodes:
			nodes[mention] = {}
			nodes[mention]["name"] = mention
			nodes[mention]["done"] = False
			nodes[mention]["type"] = "mention"
			nodes[mention]["no_messages"] = 0

		edge = chat + "_+++_" + mention

		edges[edge] = {}
		edges[edge]["name"] = edge
		edges[edge]["weight"] = mentions[mention]


	for domain in domains:

		if domain not in nodes:
			nodes[domain] = {}
			nodes[domain]["name"] = domain
			nodes[domain]["done"] = True
			nodes[domain]["type"] = "domain"
			nodes[domain]["no_messages"] = 0

		edge = chat + "_+++_" + domain

		edges[edge] = {}
		edges[edge]["name"] = edge
		edges[edge]["weight"] = domains[domain]


	#print(domains)

	nodes[chat]["done"] = True
	nodes[chat]["no_messages"] = len(messagelist)

name = "anon"
api_id = 
api_hash = ''

# "bant4chan" (too big)
chats = ["HansTerrorwave","WhitesOnlyLounge","FascistLibrary","WhiteIsRight","CIGtelegram","TERRORWAVEREFINED","thirdpositionmemesquad","BellumActaNews","Uncle_Paul1488","randomanonch","RandomMeetingPoint","FreeHelicopterRides","Nieuwshoorn","sgmeme","Neonrightmemes","reactionary","RedPills","Multiculturalism","rightwingdeathsquad","TINPS","End_Cultural_Marxism"]
# "DankestChannel","AnarchoVaporism","CummieChannel","MyDadDidntLoveMe","AnarchistInsights","TheGulag","LeftBlock_Chat","DecentralizedPirates" (not found)
#chats = ["Moloko_Plus","AnarchoMemes","Leftygram","LeftBlock","MagicAntiPatriarchy","LeftistMemes","ZestyMemes","RevolutionaryBooks","BreadInc","PropagandaPosters","ShitLibertarianSsay","AnCapism","Lostboyevsky","PhilosophicalMusings","Leftism","RedMemesOfMars","autismopuro","UnioneSocialistadelWeb","ThePRoT","LibSoc","Propositions","AnAndFriends","ParlonsAnarchisme","Red_Politik","TitosChannel","Autonomism","ActualMarxists","LeftistBooks","PRoTEnEspanol","HegelsButWhole","ContyTeens"]
get_images = False
maxdepth = 1

nodes = {}
edges = {}

for chat in chats:
	processchats(chat)

for i in range(maxdepth):
	runnodes = dict(nodes)
	for runnode in runnodes:
		if runnodes[runnode]["done"] is not True:
			processchats(runnode)


gdfout = "nodedef>name VARCHAR,label VARCHAR,title VARCHAR,type VARCHAR,no_messages INT\n"
for node in nodes:
	if nodes[node]["done"] is True:
		gdfout += nodes[node]["name"] + "," + nodes[node]["name"] + "," + nodes[node]["name"] + "," + nodes[node]["type"] + "," + str(nodes[node]["no_messages"]) + "\n"

gdfout += "edgedef>node1 VARCHAR,node2 VARCHAR, directed BOOLEAN, weight DOUBLE\n"
for edge in edges:
	edgepair = edges[edge]["name"].split("_+++_")
	gdfout += edgepair[0] + "," + edgepair[1] + ",true," + str(edges[edge]["weight"]) + "\n"

f = open("network.gdf", 'w')
f.write(gdfout)