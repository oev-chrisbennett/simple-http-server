import socket


def main() -> None:
    print("Server is running on port 4221")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, client_address = server_socket.accept()

    client_socket.recv(1024) # Buffer size of 1024 bytes

    response = "HTTP/1.1 200 OK\r\n\r\n"
    client_socket.sendall(response.encode())

    client_socket.close()


if __name__ == "__main__":
    main()
