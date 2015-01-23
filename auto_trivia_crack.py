#!/usr/bin/env python

import requests
import json
import sys
import getpass

base = 'http://api.preguntados.com/api/users/'

def send_request(method,url,session_id,d=None):
    req = requests.Request(method,url,cookies={'ap_session':session_id})
    if d != None:
        req = requests.Request(method,url,cookies={'ap_session':session_id},json=d)
    r = req.prepare()
    s = requests.Session()
    return s.send(r)

def login(email,password):
    r = send_request('POST','http://api.preguntados.com/api/login','',d={'email':email,'password':password});
    return (r.headers['Set-Cookie'],str(r.json()['id']),)

def get_questions(user_id, game_id, session_id):
    url = base+user_id+'/games/'+game_id
    r = send_request('GET',url,session_id)
    return r

def get_games(user_id,session_id):
    url = base+user_id+'/dashboard'
    r = send_request('GET',url,session_id)
    return r

def answer_question(user_id,game_id,session_id,answer):
    url = base+user_id+'/games/'+game_id+'/answers'
    r = send_request('POST',url,session_id,d=answer)
    return r

content = []
try:
    with open('settings.conf') as f:
        content = f.readlines()
except:
    print("Failed to read \"settings.conf\"!")
    sys.exit(1)

user_id=None
settings = json.loads(content[0])
if settings['ap_session']=='':
    email = input("Email: ")
    password = getpass.getpass()
    (session_id,user_id) = login(email,password)
    session_id = '='.join(session_id.split('=')[1:])
else:
    session_id=settings['ap_session']

if user_id == None:
    if settings['user_id'] == '':
        print("Enter the user id of the player.")
        user_id = input()
    else:
        user_id = settings['user_id']

dash = get_games(user_id,session_id)
if dash.status_code != 200:
    print("An error has ocurred. The status code is "+str(dash.status_code))
    print("Check the ap_session cookie, it may have been invalidated or may not match the user_id you're using")
    sys.exit(1)

dash_js = dash.json()
print("Your current active games are:")
for game in dash_js['list']:
    if game['game_status'] not in ('ACTIVE','PENDING_APPROVAL'):
        continue
    turn = ' '
    if not game['my_turn']:
        turn = 'NOT '

    print('Game: '+str(game['id'])+' vs. '+game['opponent']['username']+' is '+game['game_status']+' it is '+turn+ 'my turn')

if settings['game_id']=='':
    print("Enter a game-id to auto-play or 0 to quit:")
    game_id = input()
else:
    game_id = settings['game_id']
if game_id == '0':
    print('Quitter...')
    sys.exit(0)

correct = 0;

while(True):
    questions = get_questions(user_id,game_id,session_id)
    #print (questions.status_code)
    if questions.status_code != 200:
        print("I couldn't get the questsions!")
        sys.exit(1)

    q_js = questions.json()
    
#    if not q_js['game_status']=='ACTIVE':
#        print('This game is no longer active!')
#        break;
	
    if q_js['game_status']=='ENDED':
        print('This game is over! I bet you I won :D')
        break;

    if not q_js['my_turn']:
        print("It is not your turn. This game cannot be played!")
        break;
    else:
        spin = q_js['spins_data']['spins'][0]
        spin_type = spin['type']
#        if spin['type'] == 'NORMAL':
#        #not crown spin
        if spin['type'] == 'CROWN':
            print("FOR A CROWN")
        question = spin['questions'][0]['question']
        q_id=question['id']
        q_category=question['category']
        q_text=question['text']
        q_answer=question['correct_answer']
        q_answers=question['answers']
        q_type = question['media_type']
        print("The question is: "+q_text)
        print("The answers are")
        for q in q_answers:
            print("\t"+q)
        print("The correct answer is: "+q_answers[q_answer])
        
        answer = {'answers':[{'id':q_id,'category':q_category,'answer':q_answer}],'type':spin_type}
        r = answer_question(user_id,game_id,session_id,answer)
        if r.status_code == 400:
            print('The server told me \"'+r.json()['message']+'\" so fun is over for now... :(')
            sys.exit(0)

        #print(r.status_code)
        #print(r.json())
        if r.json()['my_turn']:
            print("Yup, got it right")
            correct+=1
        else:
            print("Something happened and it isn't my turn any more (maybe got swapped for having too many characters in first round?)")
#        else:
#            #crown spin
#            print("I don't know how to handle a crown yet, so I'm not going to try")
#            break;
        print('')

print("I got "+str(correct)+" right before something happened")
