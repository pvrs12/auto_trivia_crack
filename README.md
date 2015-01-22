# auto_trivia_crack
A program which is designed to automagically play a single game of trivia crack, getting every question correct.

The settings.conf file is a json file which contains several possible settings for the script.

* ap_session
  * This is from the cookie that authenticates the user with trivia crack
  * If left blank the user will be prompted for an email and password
  * It can be filled to support other login methods, like facebook
* user_id
  * This is the id for who to play as on trivia crack
  * The user_id must be the one which is paired with the ap_session, or you will get 403 errors
  * If left blank the program will either get the user_id from trivia crack (if ap_session is also blank) or will prompt the user for a user_id
* game_id
  * This is the id for which game you will be playing on trivia crack
  * If left blank, the program will list the available games and the user will be prompted
  
**A note on passwords**

The password you provide to this program is not stored in anyway by this program. It is however passed in plain text and not even masked on the input to the console.
Additionally, the trivia crack api uses insecure http so any password you provide to it is passed in clear-text over the network. Be Careful.