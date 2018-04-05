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

# Buffer to store the received data
# Checking with while loop
def checkBuffer(checksocket, inBytes):

    inititalBuff = ''

    while (inBytes > len(inititalBuff)):

        tmpBuff = checksocket.recv(inBytes).decode(convertBits)

        if not tmpBuff:
            break

        inititalBuff += tmpBuff

    return inititalBuff

##########################################

# Create a TCP socket
def tempSocket(client):

    welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket
    try:
        welcomeSocket.bind(('', 0))
    except socket.error as errors:
        print("Binding failed with Code: ", str(errors))
        return None

    PortNum = welcomeSocket.getsockname()[1]
    print('Ephemeral port # is: ', PortNum)
    client.send(str(PortNum).encode(convertBits))

    # Forever accept incoming connections
    welcomeSocket.listen(1)
    print ("Server is ready to receive. ")
   
    # Accept a connection; get client's socket
    (ClientSock, ip) = welcomeSocket.accept()
    
    # Close the socket
    welcomeSocket.close()

    return ClientSock

##########################################

# Receive a file from client by server
# Used for 'put <filename>'
def revFile(textFile, welcomeSocket):

    SizeBuff = checkBuffer(welcomeSocket, 10)

    # Get size of buffer and check for errors
    if SizeBuff == '':
        print("Receiving errors. ")
        return 0
    else:
        RealSize = int(SizeBuff)

    print ("Size: ", RealSize)

    readingfile = checkBuffer(welcomeSocket, RealSize)

    # Prepare to write
    fw = open(textFile, 'w+')
    # Write as long as size of file
    fw.write(readingfile)

    fw.close()

#############################################

# Download file from sever by client
# Used for 'get <filename>'
def DownloadFile (textFile, welcomeSocket):

    # Check if you can open the file
    try:
        myFile = open(textFile, 'r')
    except OSError:
        print("Failed to open this file: ", textFile)
        welcomeSocket.close()

        print ("Now sending the file name: ", textFile)

    fileData = None
    numSent = 0

    # Check if you can read from file; make sure it's the right size
    # Acquire data
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

        print('Sent ', numSent, ' bytes. ')

    myFile.close()
    welcomeSocket.close()

    return True

##############################################################################

# Downloads file from the server
def getting(clientS, textFile):

    tempS = tempSocket(clientS)

    done = DownloadFile(textFile, tempS)
    if done:
        print("Start to download file: ", textFile)
        rev = clientS.recv(1).decode(convertBits)
        if rev == '1':
            print("Dowload completed: ", textFile)
        else:
            print("Fail to Download: ", textFile)
    else:
        print("Fail to rev a file from server ", textFile)

    tempS.close()

# Uploads file to the server
def putting ( clientS, textFile ):
        tempS = tempSocket(clientS)

        done = revFile(textFile, tempS)
        if done == 0:
            print('Failed to upload file: ', textFile)
            clientS.send('0'.encode(convertBits))
        else:
            print('Upload completed: ', textFile)
            clientS.send('1'.encode(convertBits))
        tempS.close()

# Lists files on the server
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
        i = i + 1
    data_file= pickle.dumps(all_files)

    tempS.send(data_file)
    tempS.close()

# Disconnects from the server and exits
def quiting(clientS):
        print("Fin connection now. ")
        clientS.close()
        exit(1)

##############################################################################

# Main
def main():

    if len(sys.argv) < 2:
        print ("python " + sys.argv[0] + "<port_number>")

    serverPort = int(sys.argv[1])

    serverS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Socket ready to use. ")

    try:
        serverS.bind((serverName, serverPort))
    except socket.error as errors:
        print("Binding failed with Code: ", str(errors))

        serverS.close()
        return

    print("Bind complete. ")

    serverS.listen(request_queue)

    print("Listening to client... ")

    while True:
        print('Server is waiting for connection...')

        (clientS, ip) = serverS.accept()
        print('One client connected with IP: ', ip, ' from the port #: ', serverPort)
        while True:
            command = clientS.recv(bufferSize).decode(convertBits)

            if not command:
                print("Wrong command from client. ")
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
                print("Incorrect command from user !")

if __name__ == "__main__":
    main()

