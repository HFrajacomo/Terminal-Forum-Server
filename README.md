
# Terminal Server

A multi-platform secure distributed system capable of real-time chatting, forum posting and file sharing.

## Functionalities

- Distributed client and server
- Authentication Server
- Client auto-updater and support to mods
- Account login system
- Forum posts management
- Real-time chat with text color and commands
- File sharing with secure FTP connection
- Admin Commands
- Secure to either host and user

## Requirements

- Python 3 (should be default installation of Python)
- Windows 10 or Linux 3.0-rc1 (or superior) or MacOS

## Instalation

Server and client:
``` sh
$ git clone <this repo>
```
Client only:
**Download Forum.py file**

## Running
### Client
To use the program as a user, run Forum.py and follow the instructions described on the program.
This is the only file you need from this project to access servers.

```sh
$ python Forum.py
```

### Server
To run a server, execute the server.py file and then, in a fresh terminal, run update_server.py, in this order.

```sh
$ python server.py
$ python update_server.py
```

The file **ip.txt** will be generated. Insert your external IP onto the file to open a network connection, or leave it blank to access localhost. If you are using external network connection **port forward ports 33000 until 33003**.

Re-run the scripts to host your server.

# Architecture

This project follows the "Publish-Subscribe" architecture of distributed system. A wrapper is used in the user application to enforce security and mod support for server owners.

![](Images/Architecture.jpg)

## Auto Updater
Every server owner has the option of distributing the vanilla client or a modded one. In any case, we got you covered. Everytime a user joins a server, it will check for updates in the client version the user has.

In case of an outdated/different version, the auto-uploader will download the new client and run it without any user input.

## Login
Congratulations, you joined a server. Now you must create an account. An account is your digital identification. You can either create a new account, or login to an existing one.

An account can be an user account, or an admin account, the latter one is granted privileges and commands.

All user accounts are stored in the server files. A server owner can manipulate an account in case it finds the need to (deleting, changing offensive names, promoting or demoting, etc.).

*Commands:*
- **/l (username) (account)** to log into an account
- **/c (username) (account)** to create a new account
- **/q** to quit the server

## Forum
The forum is a place for users to create different conversation topics and send messages to them. Users are allowed to create, write a read topics. Admin accounts can delete a topic, if they wish to.

One can see all existing topics by using the **posts** command.
To write to a topic, use: **write (topic) (message)**.
Reading a topic is tricky. Since it can have hundreds of messages, they were broken down into pages with 10 messages each. Reading works like: **read (topic) (pagenum=0)**, where pagenum is the number of the page you want to read. 0 is the latest page and is also a default value if the user doesn't specify pagenum.
An admin can also do **delete_post (topic)** to erase an entire topic forever.

## Chat
A chat is a place where you can message a group of people in real-time. To join the chat, type **chat** in the menu.

Chatting works as simple as possible. You write what you want and hit ENTER to send. No biggy. Every user has a text color as well, so that it doesn't look boring.

The messages are labelled with the sender's username and time stamp of arrival.

You can venture into the chat commands if they want:
- **/q** quits the chat.
- **/w** checks who's online onto the chat.
- **/c** clears chat window locally.
- **/cc** changes self text color in chat.
- **/h** displays a help message for chat commands.
- **/k (username)** to remove an user from chat forcibly. *(admin only)*

Also, a help message will be displayed every few messages sent.

## File services
One can use the server as a upload/download service. All users can upload files and all users can download these files. For that, it's useful to know a few commands:

- **files** shows the files available in the server, the user who posted it, the size and the date and time posted.
- **upload (filename)** uploads a file to the server. Notice that the default upload directory is the Desktop folder. One can change the default directory in the file **config.cfg**.
- **download (filename)** downloads a file from the server. The defaut download directory is the application folder. One can change it in the **config.cfg** file.

## Authentication
Everytime a user tries to connect to a server, an authentication code is generated. This code is used to block malicious attempts to connect to a server with a modified/unauthorized client.

To join servers, the user has to use the Forum.py client application wrapper. Any attempts to log into any server through the client.py file on it's own, even if not modded, will result in a malicious connection block.

## Modding
### Server modding
Servers can be modded by the owner simply by tweaking the server.py file. One can add new functionalities to their server or tweak peculiarities to their taste. 
Modding a server has **no limits or protection**. So, as a user, join trusted servers only!

### Authorized client modding
The default client of a server can be modded by the server owner. There's no restriction to what a server owner can do at this point. To mod and set the new client as default on the server, tweak the client.py file inside the folder **Updated Client**.

### Unauthorized client modding
Any modding coming from the client-side is unauthorized and disencouranged. Servers are linked to authentication servers that **will refuse connections of unauthorized clients**.
One might find quite annoying the implications of unathorized accesses. You might not want to try it.  