from __future__ import print_function
import socket
import subprocess
import sys
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
    fileData = None
    numSent = 0
    while True:
        fileData = myFile.read()

        if fileData:


            dataSizeStr = str(len(fileData))


            while len(dataSizeStr) < 10:

                dataSizeStr = "0" + dataSizeStr

            fileData = dataSizeStr + fileData



            while len(fileData) > numSent:
                numSent += welcomeSocket.send(fileData[numSent:].encode(convertBits))

        else:
            break

        print('Sent', numSent, 'bytes.')



    myFile.close()
    welcomeSocket.close()

    return True

##############################################################################

def putting ( clientS, textFile ):
        tempS = tempSocket(clientS)

        done = revFile(textFile, tempS)
        if done == 0:
            print('Fail to upload file', textFile)
            clientS.send('0'.encode(convertBits))
        else:
            print('Uploaded compteled', textFile)
            clientS.send('1'.encode(convertBits))
        tempS.close()


def getting(clientS, textFile):

    tempS = tempSocket(clientS)

    done = DownloadFile(textFile, tempS)
    if done == 0:
        print('Fail to download file', textFile)
        clientS.send('0'.encode(convertBits))
    else:
        print('dowload compteled', textFile)
        clientS.send('1'.encode(convertBits))

    tempS.close()


def quiting(clientS):
        print("Fin connection now")
        clientS.close()
        exit(1)

def lsing(cmd, clientS):
    tempS = tempSocket(clientS)

    directory=[]

    all_files = []

    for line in subprocess.getstatusoutput(cmd):
        directory.append(line)

    all_files = directory[1].split('\t')
    i = 0
    for singlefile in all_files:
        if singlefile == serverSource:
            del all_files[i]
        i = i+1
    data_file= pickle.dumps(all_files)

    tempS.send(data_file)

    tempS.close()
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
                print("Wrong command from client")
                break

            clientCmd = command.count(' ')

            if clientCmd == 1:
                (cmd, textFile) = command.split()
            elif clientCmd == 0:
                cmd = command

            if cmd == 'put' and clientCmd == 1:
                 putting(clientS, textFile)

            elif cmd == 'get' and clientCmd == 1:
                getting(clientS,textFile)

            elif cmd == 'quit' and clientCmd == 0:
                quiting(clientS)
                
            elif cmd == 'ls' or cmd =='dir' and clientCmd == 0:
                lsing(cmd, clientS)

            else:

                print("Incorrect command from user !!!!")

if __name__ == "__main__":
    main()



