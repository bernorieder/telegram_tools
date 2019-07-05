from telethon.sync import TelegramClient
import os.path
import json

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
name = "anon"
api_id = 803086
api_hash = 'ad05698671e89715aa722e49cb4901a8'

#chat = "WhiteIsRight"
chat = "noticiascaracol"
get_images = False



folder = "./" + chat + "/"
if not os.path.exists("./"+chat+"/"):
	os.makedirs(folder)

messagelist = []

with TelegramClient(name, api_id, api_hash) as client:
	for msg in client.iter_messages(chat):
		
		#print(msg)

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

with open(chat + ".json", "w") as outfile:
	json.dump(messagelist, outfile)