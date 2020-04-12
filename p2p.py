"""
George Fayette
Multi-Party P2P Chat
4-1-2020

This program continuously listens for new incoming p2p connections.
Each connection uses 2 sockets, one for sending messages and one
for receiving messages.

The user may initiate a new connection by pressing 'C' and entering
an IP address and port number. Messages entered by the user are sent
to all connected peers.

Possible improvement - Relay new incoming connections to all currently
connected peers to automatically create a distributed group chat.
"""

import socket
from threading import Thread
from emojis import emojis


def listen_to_socket(send_socket, receive_socket, name):
    while True:
        message = receive_socket.recv(1024).decode()
        if message.upper() == 'X':
            print(name + ' has left the chat.')
            receive_socket.close()
            try:
                send_socket.sendall(message.encode())
                send_socket.close()
            except Exception:
                send_socket.close()
            break
        if message != '':
            print(emojis.encode(name + '\t' + message))


def establish_connection(send_socket, receive_socket, name):
    send_socket.sendall(name.encode())
    friend_name = receive_socket.recv(1024).decode()
    print(friend_name + ' has entered the chat.')

    listen_thread = Thread(target=listen_to_socket, args=(send_socket, receive_socket, friend_name,))
    listen_thread.start()


def start_connection(name, sockets):
    user_input = input('Enter IP and port number:\n')
    try:
        host, port = user_input.split()
        receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receive_socket.connect((host, int(port)))
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_socket.connect((host, int(port)))

        sockets.append(send_socket)
        establish_connection(send_socket, receive_socket, name)
    except Exception:
        print("Connection to " + user_input + " was unsuccessful.")


def listen_for_new_connections(name, send_sockets):
    new_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_connection_socket.bind(('', 0))
    new_connection_socket.listen()
    print('Listening for new connections on', (socket.gethostbyname(socket.gethostname()),
                                               new_connection_socket.getsockname()[1]))
    while True:
        try:
            send_socket, address = new_connection_socket.accept()
            receive_socket, address = new_connection_socket.accept()
            send_sockets.append(send_socket)
            establish_connection(send_socket, receive_socket, name)
        except KeyboardInterrupt:
            new_connection_socket.close()
            break


def handle_input(send_socks, name):
    while True:
        message = input()
        if message.upper() == 'C':
            start_connection(name, send_socks)
        elif message.upper() == 'X':
            print('Closing connections.')
            for send_socket in send_socks:
                try:
                    send_socket.sendall(message.encode())
                    send_socket.close()
                except Exception:
                    send_socket.close()
            break
        elif message != '':
            print(emojis.encode(name + '\t' + message))
            for send_socket in send_socks:
                try:
                    send_socket.sendall(message.encode())
                except Exception:
                    send_socket.close()


def main():
    name = input('Enter your name:\n')
    print('Hello ' + name + '!')
    print('Press C to connect, X to close all connections, and CTRL+C to stop listening for new connections.')
    send_sockets = []
    input_thread = Thread(target=handle_input, args=(send_sockets, name,))
    input_thread.start()
    listen_for_new_connections(name, send_sockets)


if __name__ == '__main__':
    main()
