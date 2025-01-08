# General info 
* This use python TUF to create a secure update framework for application update.
* The test application is color_changer.py
* Build the color_changer.py or any other application you choose to an .exe together with the updater.py and launcher.py.
* The launcher is what calls the rest of the .exe file to run.
* Make changes to the BASE_URL variable if its local server or remote server. For this the server_host.py is hosted on a remote server or run locally.
* Remember to change your DB_NAME to which every name you want or leave the default. 
* Having an .env file with the proper variable is important for the files to run.
* This has a custom-made progress hook made with tkinter. you can change to which ever progress hook that suits you
* A copy of the target would need in the download folder for it not to be to update everytime the app is lunched. 

# <b>NB:</B>  
* This use mongodb gridfs as database. you can choose to use any database of your choice.
* If you want to run the tuf update flow on program file folder with elevated right see privileged branch.


# News
* If you have any problems regarding the script, or you need my services email me at: [wolfs.code.work@gmail.com](mailto:wolfs.code.work@gmail.com)

