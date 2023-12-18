import socket


def main() -> None:
    print("Server is running on port 4221")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, client_address = server_socket.accept()

    request = client_socket.recv(1024).decode()

    first_line = request.split("\n")[0]
    method, path, protocol = first_line.split(" ")

    if path == "/":
        response = b"HTTP/1.1 200 OK\r\n\r\nHello, World!"
    elif path.startswith("/echo"):
        message = path.lstrip("/echo/")
        headers = f"HTTP/1.1 200 O K\r\nContent-Type: text/plain\r\nContent-Length: {len(message)}\r\n\r\n"
        response = (headers + message).encode()
    else:
        response = b"HTTP/1.1 404 Not Found\r\n\r\n"

    client_socket.sendall(response)
    client_socket.close()


if __name__ == "__main__":
    main()
