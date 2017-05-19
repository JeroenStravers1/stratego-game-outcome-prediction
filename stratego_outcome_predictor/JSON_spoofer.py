import requests
import json

init_source = "init"
init_target = "init"

init_positions = [["E","E","B","M","B","E","F","B","D","E"],["B","G","I","B","H","G","B","I","D","E"],["G","J","D","F","D","H","C","D","J","G"],["D","H","D","L","I","F","K","F","D","H"],["A","A","_","_","A","A","_","_","A","A"],["A","A","_","_","A","A","_","_","A","A"],["R","N","T","O","P","T","W","N","P","S"],["P","N","V","P","V","P","S","P","U","X"],["N","Q","T","Q","Q","P","Y","R","N","N"],["R","Q","U","P","T","S","Q","S","U","R"]]

init_unmoved = [["E","E","B","M","B","E","F","B","D","E"],["B","G","I","B","H","G","B","I","D","E"],["G","J","D","F","D","H","C","D","J","G"],["D","H","D","L","I","F","K","F","D","H"],["A","A","_","_","A","A","_","_","A","A"],["A","A","_","_","A","A","_","_","A","A"],["R","N","T","O","P","T","W","N","P","S"],["P","N","V","P","V","P","S","P","U","X"],["N","Q","T","Q","Q","P","Y","R","N","N"],["R","Q","U","P","T","S","Q","S","U","R"]]

init_unrevealed = [["E","E","B","M","B","E","F","B","D","E"],["B","G","I","B","H","G","B","I","D","E"],["G","J","D","F","D","H","C","D","J","G"],["D","H","D","L","I","F","K","F","D","H"],["A","A","_","_","A","A","_","_","A","A"],["A","A","_","_","A","A","_","_","A","A"],["R","N","T","O","P","T","W","N","P","S"],["P","N","V","P","V","P","S","P","U","X"],["N","Q","T","Q","Q","P","Y","R","N","N"],["R","Q","U","P","T","S","Q","S","U","R"]]


update_source = "A4"
update_target = "A5"
update_positions = [["E","E","B","M","B","E","F","B","D","E"],["B","G","I","B","H","G","B","I","D","E"],["G","J","D","F","D","H","C","D","J","G"],["A","H","D","L","I","F","K","F","D","H"],["D","A","_","_","A","A","_","_","A","A"],["A","A","_","_","A","A","_","_","A","A"],["R","N","T","O","P","T","W","N","P","S"],["P","N","V","P","V","P","S","P","U","X"],["N","Q","T","Q","Q","P","Y","R","N","N"],["R","Q","U","P","T","S","Q","S","U","R"]]

update_unmoved = [["E","E","B","M","B","E","F","B","D","E"],["B","G","I","B","H","G","B","I","D","E"],["G","J","D","F","D","H","C","D","J","G"],["A","H","D","L","I","F","K","F","D","H"],["A","A","_","_","A","A","_","_","A","A"],["A","A","_","_","A","A","_","_","A","A"],["R","N","T","O","P","T","W","N","P","S"],["P","N","V","P","V","P","S","P","U","X"],["N","Q","T","Q","Q","P","Y","R","N","N"],["R","Q","U","P","T","S","Q","S","U","R"]]

update_unrevealed = [["E","E","B","M","B","E","F","B","D","E"],["B","G","I","B","H","G","B","I","D","E"],["G","J","D","F","D","H","C","D","J","G"],["A","H","D","L","I","F","K","F","D","H"],["D","A","_","_","A","A","_","_","A","A"],["A","A","_","_","A","A","_","_","A","A"],["R","N","T","O","P","T","W","N","P","S"],["P","N","V","P","V","P","S","P","U","X"],["N","Q","T","Q","Q","P","Y","R","N","N"],["R","Q","U","P","T","S","Q","S","U","R"]]
 



update_source2 = "E7"
update_target2 = "E6"
update_positions2 = [["E","E","B","M","B","E","F","B","D","E"],["B","G","I","B","H","G","B","I","D","E"],["G","J","D","F","D","H","C","D","J","G"],["A","H","D","L","I","F","K","F","D","H"],["D","A","_","_","A","A","_","_","A","A"],["A","A","_","_","P","A","_","_","A","A"],["R","N","T","O","A","T","W","N","P","S"],["P","N","V","P","V","P","S","P","U","X"],["N","Q","T","Q","Q","P","Y","R","N","N"],["R","Q","U","P","T","S","Q","S","U","R"]]

update_unmoved2 = [["E","E","B","M","B","E","F","B","D","E"],["B","G","I","B","H","G","B","I","D","E"],["G","J","D","F","D","H","C","D","J","G"],["A","H","D","L","I","F","K","F","D","H"],["A","A","_","_","A","A","_","_","A","A"],["A","A","_","_","A","A","_","_","A","A"],["R","N","T","O","A","T","W","N","P","S"],["P","N","V","P","V","P","S","P","U","X"],["N","Q","T","Q","Q","P","Y","R","N","N"],["R","Q","U","P","T","S","Q","S","U","R"]]

update_unrevealed2 = [["E","E","B","M","B","E","F","B","D","E"],["B","G","I","B","H","G","B","I","D","E"],["G","J","D","F","D","H","C","D","J","G"],["A","H","D","L","I","F","K","F","D","H"],["D","A","_","_","A","A","_","_","A","A"],["A","A","_","_","P","A","_","_","A","A"],["R","N","T","O","A","T","W","N","P","S"],["P","N","V","P","V","P","S","P","U","X"],["N","Q","T","Q","Q","P","Y","R","N","N"],["R","Q","U","P","T","S","Q","S","U","R"]]


init_payload = {
    "piece_positions": json.dumps(init_positions),
    "unmoved_pieces": json.dumps(init_unmoved),
    "unrevealed_pieces": json.dumps(init_unrevealed),
    "source": json.dumps(init_source),
    "target": json.dumps(init_target)
}

update_payload = {
    "piece_positions": json.dumps(update_positions),
    "unmoved_pieces": json.dumps(update_unmoved),
    "unrevealed_pieces": json.dumps(update_unrevealed),
    "source": json.dumps(update_source),
    "target": json.dumps(update_target)
}

update2_payload = {
    "piece_positions": json.dumps(update_positions2),
    "unmoved_pieces": json.dumps(update_unmoved2),
    "unrevealed_pieces": json.dumps(update_unrevealed2),
    "source": json.dumps(update_source2),
    "target": json.dumps(update_target2)
}

#print payload["piece_positions"]

content_type = {"Content-Type": "application/json"}

#url_view = "http://127.0.0.1:5000/view"
#url_update = "http://127.0.0.1:5000/update"
#url_new_game = "http://127.0.0.1:5000/new_game"

url_view = "http://strategoboard.cloudapp.net/view/"
url_update = "http://strategoboard.cloudapp.net/update"
url_new_game = "http://strategoboard.cloudapp.net/new_game"

# new game
#r = requests.post(url_new_game, headers=content_type, data=json.dumps(init_payload))

# update
r2 = requests.post(url_update, headers=content_type, data=json.dumps(update_payload))

#r22 = r2 = requests.post(url_update, headers=content_type, data=json.dumps(update2_payload))

# view
#r3 = requests.get(url_view)

#quit()

#import time

#new game = requests.post(url_new_game, headers=content_type, data=json.dumps(init_payload))

#time.sleep(5)

#update_first = requests.post(url_update, headers=content_type, data=json.dumps(update_payload))

#time.sleep(5)

#update_second = requests.post(url_update, headers=content_type, data=json.dumps(update2_payload))







