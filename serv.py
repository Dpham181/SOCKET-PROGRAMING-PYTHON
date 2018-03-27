from __future__ import print_function
import socket
import subprocess
import sys
import os
import pickle

bufferSize = 4096
request_queue = 10
serverName = 'localhost'
convertBits = 'UTF-32'
serverSource = 'serv.py'

##########################################

# checking buffer with for loop

def checkBuffer(sock,inBytes):

    inititalBuff = ''

    while len(inititalBuff) < inBytes:

        tmpBuff = sock.recv(inBytes).decode(convertBits)

        if not tmpBuff:
            break

        inititalBuff += tmpBuff

    return inititalBuff

##########################################

# Attemping temporary socket


def tempSocket(client):

    welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        welcomeSocket.bind(('', 0))
    except socket.error as errors:
        print("Binding failed with Code:", str(errors))
        return None

    PortNum = welcomeSocket.getsockname()[1]
    print('Ephemeral port # is', PortNum)

    client.send(str(PortNum).encode(convertBits))

    welcomeSocket.listen(1)

    (ClientSock, ip) = welcomeSocket.accept()

    welcomeSocket.close()

    return ClientSock





##########################################


# receive a file from client

def revFile ( textFile,welcomeSocket ):

    SizeBuff = checkBuffer(welcomeSocket, 10)

    # Get the file size
    if SizeBuff == '':
        print("Receiving Errors.")
        return 0
    else:
        RealSize = int(SizeBuff)

    print ("size.", )
    # Get the file data
    fileData = checkBuffer(welcomeSocket, textFile)

    # Open file to write to
    fW = open(textFile, 'w+')

    # Write received data to file
    fW.write(textFile)

    # Close the file
    fW.close()


#############################################


# download file from sever by client

def DownloadFile ( textFile, welcomeSocket):

    try:
        myFile = open(textFile, 'r')
    except OSError:
        print("Fail to open this file:", textFile)
        welcomeSocket.close()

    with myFile:

	print ("now sending the fife name" + textFile)
	textSize = myFile.read()

    SizeofText= str(len(textSize))

    RealSizeofText = len(SizeofText)

    while RealSizeofText < 10:

	textSize ='0'+textSize

	textSize = textSize + len(myFile.read())


	NumTextSent= 0

	while RealSizeofText > NumTextSent:

	    NumTextSent += welcomeSocket.send(textFile[NumTextSent:].encode(convertBits))




	if NumTextSent == 0:
	    print ("sent error")
        myFile.close()
	welcomeSocket.close()

##############################################################################

def swicher(cmd):
    cmd = ''



##############################################################################


# Main

def main():

    if len(sys.argv) < 2:
        print ("python " + sys.argv[0] + "<port_number>")

    serverPort = int(sys.argv[1])

    serverS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Socket be ready to use. ")

    try:
        serverS.bind((serverName, serverPort))
    except socket.error as errors:
        print("Binding failed with Code:", str(errors))

        serverS.close()
        return

    print("Completing blind")

    serverS.listen(request_queue)

    print("listening to Client")

    while True:
        print('Now Server is waiting connection...')

        # Block until connection is received
        (clientS, ip) = serverS.accept()


if __name__ == "__main__":
    main()



