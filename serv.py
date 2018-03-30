from __future__ import print_function
import socket
import subprocess
import sys
import os
import pickle

bufferSize = 4096
request_queue = 10
serverName = 'localhost'
convertBits = 'UTF-8'
serverSource = 'serv.py'

##########################################

# checking buffer with for loop

def checkBuffer(checksocket,inBytes):

    inititalBuff = ''

    while (inBytes > len(inititalBuff)):

        tmpBuff = checksocket.recv(inBytes).decode(convertBits)

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

def revFile(textFile,welcomeSocket):

    SizeBuff = checkBuffer(welcomeSocket,10)

    if SizeBuff == '':
        print("Receiving Errors.")
        return 0
    else:
        RealSize = int(SizeBuff)

    print ("Size.",RealSize)

    readingfile = checkBuffer(welcomeSocket, RealSize)

    fw = open(textFile, 'w+')

    fw.write(readingfile)

    fw.close()






#############################################


# download file from sever by client

def DownloadFile (textFile, welcomeSocket):

    try:
        myFile = open(textFile, 'r')
    except OSError:
        print("Fail to open this file:", textFile)
        welcomeSocket.close()
        print ("now sending the fife name",textFile)

    with myFile:


        textSize = myFile.read()

        if textSize:

            SizeofText= str(len(textSize))

            RealSizeofText = len(SizeofText)

            while RealSizeofText < 10:
                SizeofText ='0'+SizeofText

            textSize = SizeofText + len(myFile.read())


            RealSizeofText = len(textSize)


            NumTextSent = 0

            while RealSizeofText > NumTextSent:
                NumTextSent += welcomeSocket.send(textSize[NumTextSent:].encode(convertBits))

        else:

            print("Errors")
        print('Sent', NumTextSent, 'bytes.')

    myFile.close()
    welcomeSocket.close()

    return True

##############################################################################
def putting(clientS,textFile):
        tempS = tempSocket(clientS)

        success = revFile (textFile,tempS)
        if success == 0:
            print('Fail to upload file', textFile)
            clientS.send('0'.encode(convertBits))
        else:
            print('Uploaded compteled', textFile)
            clientS.send('1'.encode(convertBits))


def clientaction(cmd,clientS,textFile):
    cmd = {
        "put": putting(clientS,textFile)

    }


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

        (clientS, ip) = serverS.accept()
        print('One client connected with IP:', ip, 'from the port #:', serverPort)
        while True:
            command = clientS.recv(bufferSize).decode(convertBits)

            if not command:
                print("wrong command from client")
                break

            clientCmd = command.count(' ')
            if clientCmd == 1:
                (cmd, textFile) = command.split()
            elif clientCmd == 0:
                cmd = command

            if  clientCmd ==1:
                clientaction(cmd,clientS,textFile)




if __name__ == "__main__":
    main()



