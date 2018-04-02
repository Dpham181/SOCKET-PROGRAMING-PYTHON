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

    #loop until all files are received
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
    # Generate an ephemeral port
    print("    ", end=' ')
    tempSocket = createphmSocket(sportNum)  # function call from create socket

    # Open file
    try:
        file_object = open(fileName, 'r')
    except OSError:
        print("    ", fileName + 'cannot open.')
        tempSocket.close()
        return False

    print("    ", 'Uploading ' + fileName + ' to the server')
    while True:
        # Read data
        data = file_object.read()

        # Make sure file is not empty by reading only EOF
        if data:

            # Get the size of the data read and convert it to string
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

        # The file is completely empty
        else:
            break

        print("    ", 'Sent', byteSent, 'bytes.')

    # Close the socket and the file
    file_object.close()
    tempSocket.close()

    return True


# Function to download a file from the server over an ephemeral port #
def downloadFileFromServer(fileName, sportNum):
    # Generate an ephemeral port
    print("    ", end=' ')
    tempSocket = createphmSocket(sportNum)

    # Receive the first 10 bytes indicating the
    # size of the file
    bufferSize = recvAll(tempSocket, 10)

    # Get the file size
    if bufferSize == '':
        print("    ", 'Missing data.')
        return False
    else:
        fileSize = int(bufferSize)

    print("    ", 'The file is', fileSize, 'bytes long')

    # Get the file data
    # demux the data from the server to the client until receive buffer is full
    data = recvAll(tempSocket, fileSize)

    # Open file to write to
    fWriter = open(fileName, 'w+')

    # Write received data to file
    fWriter.write(data)

    # Close file
    fWriter.close()

    return True


# *******************************************************************
#                    MAIN PROGRAM
# *******************************************************************
def main():
    if len(sys.argv) < 2:
        print('python' + sys.argv[0] + '<server_port>')
    serverName = "ecs.fullerton.edu"
    serverPort = int(sys.argv[1])

    pSocket = createphmSocket(serverPort)

    while True:
        ans = input('ftp> ')

        # Argument counting using spaces
        ftp_arg_count = ans.count(' ')

        if ftp_arg_count == 1:
            (command, fileName) = ans.split()
        elif ftp_arg_count == 0:
            command = ans

        # Process input
        if command == 'put' and ftp_arg_count == 1:
            # Send the entire command to server: put [file]
            pSocket.send(ans.encode(codingMethod))

            # Receive an ephemeral port from server to upload the file over
            tempPort = pSocket.recv(bufferSize).decode(codingMethod)

            print("    ", 'Received the ephemeral port #', tempPort)
            success = uploadFileToServer(fileName, tempPort)

            if success:
                print("    ", 'Successfully uploaded the file')
                # Get server report
                receipt = pSocket.recv(1).decode(codingMethod)
                if receipt == '1':
                    print("    ", 'Server successfully has received file')
                else:
                    print("    ", 'Server was not able to receive the file')
            else:
                print("    ", 'Unable to upload the file')

        elif command == 'get' and ftp_arg_count == 1:
            # Send the entire command to server: get [file]
            pSocket.send(ans.encode(codingMethod))

            # Receive an ephemeral port from server to download the file over
            tempPort = pSocket.recv(bufferSize).decode(codingMethod)
            print("    ", 'Received the ephemeral port #', tempPort)

            success = downloadFileFromServer(fileName, tempPort)

            # Send success/failure notification to server
            if success:
                print("    ", 'Server has successfully downloaded the file')
                pSocket.send('1'.encode(codingMethod))
            else:
                print("    ", 'Unable to download the file')
                pSocket.send('0'.encode(codingMethod))

        elif command == 'dir' and ftp_arg_count == 0:
            # Send the entire command to server: ls
            pSocket.send(ans.encode(codingMethod))

            # Get ephemeral port generated by server
            tempPort = pSocket.recv(bufferSize).decode(codingMethod)
            print("    ", 'Received the ephemeral port #', tempPort)

            # Create ephemeral socket and wait for data
            print("    ", end=' ')
            ephmSocket = createphmSocket(tempPort)
            data = ephmSocket.recv(bufferSize)

            # Need 'pickle.loads' to extract list
            server_dir = pickle.loads(data)

            # Print out directory
            print('\n', "    " + 'Files that are on the server:')
            for line in server_dir:
                print("    ", line)

            ephmSocket.close()

        elif command == 'quit' and ftp_arg_count == 0:
            print("    ", 'Closing it now')

            pSocket.send(ans.encode(codingMethod))
            pSocket.close()
            break

        else:
            print("    ", 'Invalid command. Try: putting [file], getting [file], ls, or quit')


if __name__ == "__main__":
    main()
