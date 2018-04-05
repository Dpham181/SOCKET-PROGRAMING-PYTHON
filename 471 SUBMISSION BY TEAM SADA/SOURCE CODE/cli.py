from __future__ import print_function
from pathlib import Path
import socket
import sys
import pickle  # for receiving list data
import os.path

bufferSize = 4096
serverName = "localhost"
codingMethod = "UTF-8"


# idt$ = "    "  # Indent so that client feedback looks clean


# Receives the number of bytes arrving from a TCP socket
def recvAll(sock, numBytes):
    # declare the receive buffer
    recvBuff = ''

    # loop until all files are received
    while len(recvBuff) < numBytes:

        # initialize and declare the temporary buffer which can receives bytes
        tmpBuff = sock.recv(numBytes).decode(codingMethod)

        # if other side socket is closed
        if not tmpBuff:
            break

        # add bytes to buffer
        recvBuff += tmpBuff

    return recvBuff


# this function creates a socket utilizing a provided port number and server
def createphmSocket(sportNum):
    # this is where you create a TCP socket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # this helps us connect to the server
    clientSocket.connect((serverName, int(sportNum)))
    print('Connected to the server port # :', sportNum)

    # here we will return the created socket
    return clientSocket


# Function to upload a file to the server over an ephemeral port #
def uploadFileToServer(fileName, sportNum):
    # this is where you generate the ephemeral port
    print("    ", end=' ')
    tempSocket = createphmSocket(sportNum)  # function call from create socket

    # Open the file
    try:
        fio_object = open(fileName, 'r')
    except OSError:
        print("    ", fileName + 'cannot open.')
        tempSocket.close()
        return False

    print("    ", 'Now uploading ' + fileName + ' to the server')
    while True:
        # Read  the data
        data = fio_object.read()

        # if file is not empty by reading only EOF
        if data:

            # obtain the size and convert it to string data type
            dataSize = str(len(data))

            # Prepend 0's to the size string until the size is 10 bytes
            while len(dataSize) < 10:
                dataSize = '0' + dataSize

            # Prepend the size of the data to the
            # file data.
            data = dataSize + data

            # The number of bytes sent
            byteSent = 0

            # Send the data!
            # multiplex the data to the server until data is full
            while len(data) > byteSent:
                byteSent += tempSocket.send(data[byteSent:].encode(codingMethod))

        # The file is completely empty now
        else:
            break

        print("    ", 'Sent', byteSent, 'bytes.')

    # Close the socket and the file
    fio_object.close()
    tempSocket.close()

    return True


# Function to download a file from the server over the ephemeral port #
def downloadFileFromServer(fileName, sportNum):
    # ephmeral port is generated here
    print("    ", end=' ')
    tempSocket = createphmSocket(sportNum)

    # After receiving the first 10 bytes that indicates the size of the file
    bufferSize = recvAll(tempSocket, 10)

    # file size obtained
    if bufferSize == '':
        print("    ", 'Missing data.')
        return False
    else:
        fileSize = int(bufferSize)

    print("    ", 'The size of the file is', fileSize, 'bytes long')

    # obtaining the file data
    # demux the data from the server to the client until receive buffer is full
    data = recvAll(tempSocket, fileSize)

    # Open file and then write to file
    fWriter = open(fileName, 'w+')

    # Write data to the file
    fWriter.write(data)

    # Close file
    fWriter.close()

    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                    MAIN PROGRAM STARTS HERE
# *~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    if len(sys.argv) < 2:
        # if command line has less than 2 arguments,
        print('python' + sys.argv[0] + '<server_port>')
        # illustrate how to enter the server port to connect to server

    serverName = "ecs.fullerton.edu"
    serverPort = int(sys.argv[1])
    # user inputs the server port for the print message above

    # create an socket for the server port and label as the primary socket
    pSocket = createphmSocket(serverPort)

    # loop until user enters quit
    while True:
        ans = input('ftp> ')
        # Write a command after ftp> print

        # Argument counting is space sensitive
        ftp_arg_count = ans.count(' ')

        if ftp_arg_count == 1:
            (command, fileName) = ans.split()
            # split the commands if more than one word to command and then filename
        elif ftp_arg_count == 0:
            command = ans
            # one string long command is

        # Input command
        if command == 'put' and ftp_arg_count == 1:
            # The put [file]command is sent to server
            pSocket.send(ans.encode(codingMethod))

            # client receives the ephemeral port address from the server to upload the file over
            tempPort = pSocket.recv(bufferSize).decode(codingMethod)

            print("    ", 'Gotcha! Obtained the ephemeral port #', tempPort)
            uploaded = uploadFileToServer(fileName, tempPort)

            if uploaded:
                print("    ", 'Completed uploading the file')
                # Get the server status
                receipt = pSocket.recv(1).decode(codingMethod)
                if receipt == '1':
                    print("    ", 'Congrats, the *Server* has received the file')
                else:
                    print("    ", 'oops! Server did not receive the file')
            else:
                print("    ", 'Not able to upload the file')

        elif command == 'get' and ftp_arg_count == 1:
            # The get [file]command is sent to server
            pSocket.send(ans.encode(codingMethod))

            # client receives the ephemeral port address from the server to upload the file over
            tempPort = pSocket.recv(bufferSize).decode(codingMethod)
            print("    ", 'Gotcha! Obtained the ephemeral port #', tempPort)

            uploaded = downloadFileFromServer(fileName, tempPort)

            # Send success/failure status to the server
            if uploaded:
                print("    ", 'Congrats, the *Server* has downloaded the file!')
                pSocket.send('1'.encode(codingMethod))
            else:
                print("    ", 'dummit! Unable to download the file')
                pSocket.send('0'.encode(codingMethod))

        elif command == 'dir'or command =='ls' and ftp_arg_count == 0:
            # if file not able to download the file send the command to server: ls
            pSocket.send(ans.encode(codingMethod))

            # obtain the ephemeral port generated by the server
            tempPort = pSocket.recv(bufferSize).decode(codingMethod)
            print("    ", 'Yay! Received the ephemeral port #', tempPort)

            # ephemeral socket and is waiting for the data
            print("    ", end=' ')
            ephmSocket = createphmSocket(tempPort)
            data = ephmSocket.recv(bufferSize)

            # Extract list
            server_dir = pickle.loads(data)

            # Print directory
            print('\n', "    " + 'number of files that are on the server:')
            for line in server_dir:
                print("    ", line)

            ephmSocket.close()

        elif command == 'quit' and ftp_arg_count == 0:
            print("    ", 'ending the session now')

            pSocket.send(ans.encode(codingMethod))
            pSocket.close()
            break

        else:
            print("    ", 'not a valid command. Try: put [file], get [file], ls, or quit')


if __name__ == "__main__":
    main()
