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

    # The buffer
    recvBuff = ''

    # Keep receiving till all is received
    while len(recvBuff) < inBytes:

        # Attempt to receive bytes
        tmpBuff = sock.recv(inBytes).decode(ConvertBits)

        # The other side has closed the socket
        if not tmpBuff:
            break

        # Add the received bytes to the buffer
        recvBuff += tmpBuff

    return recvBuff

##########################################

# Attemping temporary socket


def tempSocket(client):

    welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        welcomeSocket.bind(('', 0))
    except socket.error as msg:
        print('Bind failed. Error Code :', str(msg))
        return None

    tempPortNum = welcomeSocket.getsockname()[1]
    print('Ephemeral port # is', tempPortNum)

    client.send(str(tempPortNum).encode(ConvertBits))

    welcomeSocket.listen(1)

    (tempCliSock, addr) = welcomeSocket.accept()

    welcomeSocket.close()

    return tempCliSock





##########################################


# receive a file from client

def revFile ( textFile,welcomeSocket ):

    SizeBuff = recvAll(welcomeSocket, 10)

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
        tempSocket.close()

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

	    NumTextSent += welcomeSocket.send(textFile[NumTextSent:].encode(ConvertBits))




	if NumTextSent == 0:
	    print ("sent error")

	ThisFile.close()
	welcomeSocket.close()

##############################################################################


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
    except socket.error as msg:
        print('Bind failed. Error Code:', str(msg))

        serverS.close()
        return

    print('Completing blind')

    serverS.listen(request_queue)

    print("listening to Client")


if __name__ == "__main__":
    main()



