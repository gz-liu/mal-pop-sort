# mal-pop-sort
sorts manga list by popularity to see the most obscure manga you've read for funzies. should only require pandas

how it works (for now):
1. create .env and add your mal client id/secret. when i'm not lazy it'll have its own service and interface and you don't need to add in your mal api ids
2. run the program
3. click the link in the console and authorize the app
4. once authorized, the url should have a code parameter, copy paste that id in the console
5. list output as a csv file as 'popularity_list.csv.' eventually it'll be exposed thru the web without the need of a file.
