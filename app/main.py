import os
import socket
import threading
import argparse


class HTTPServer:
    def __init__(self, host="localhost", port=4221, directory="."):
        self.host = host
        self.port = port
        self.directory = directory

    def start(self):
        with socket.create_server((self.host, self.port), reuse_port=True) as server:
            print(f"Server is running on port {self.port}")
            while True:
                client_socket, _ = server.accept()
                thread = threading.Thread(
                    target=self.handle_request, args=(client_socket,), daemon=True
                )
                thread.start()

    def handle_request(self, client_socket):
        with client_socket:
            request = client_socket.recv(1024).decode()
            method, path, headers, body = self.parse_request(request)
            response = self.create_response(method, path, headers, body)
            client_socket.sendall(response)

    def parse_request(self, request):
        request_lines = request.splitlines()
        method, path, _ = request_lines[0].split()
        headers = {
            header.split(":")[0].strip(): header.split(":")[1].strip()
            for header in request_lines[1:]
            if ":" in header
        }
        body = (
            request_lines[-1]
            if request_lines[-1] and ":" not in request_lines[-1]
            else None
        )
        return method, path, headers, body

    def construct_response(self, status, content_type, body: str):
        headers = f"HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\nContent-Length: {len(body)}\r\n\r\n"
        return (headers + body).encode()

    def create_response(self, method, path, headers, body):
        user_agent = headers.get("User-Agent")

        if path == "/":
            return self.construct_response("200 OK", "text/plain", "")
        elif path and path.startswith("/echo"):
            message = path.lstrip("/echo/")
            return self.construct_response("200 OK", "text/plain", message)
        elif path == "/user-agent":
            return self.construct_response("200 OK", "text/plain", user_agent)
        elif path.startswith("/files"):
            if method == "GET":
                return self.handle_get_file(path, headers)
            elif method == "POST":
                return self.handle_post_file(path, headers, body)
        else:
            return self.construct_response(
                "404 Not Found", "text/plain", f"{path} not found"
            )

    def handle_get_file(self, path, headers):
        file_path = os.path.join(self.directory, path.lstrip("/files/"))
        try:
            with open(file_path, "r") as file:
                return self.construct_response(
                    "200 OK", "application/octet-stream", file.read()
                )
        except FileNotFoundError:
            return self.construct_response(
                "404 Not Found", "text/plain", f"{file_path} not found"
            )

    def handle_post_file(self, path, headers, body):
        filename = path.lstrip("/files/")
        file_path = os.path.join(self.directory, filename)
        try:
            with open(file_path, "wb") as file:
                file.write(body.encode())
            return self.construct_response("201 Created", "text/plain", "")
        except Exception as e:
            return self.construct_response(
                "500 Internal Server Error", "text/plain", f"Error writing file - {e}"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--directory", default=".", help="The directory to serve files from"
    )
    args = parser.parse_args()
    server = HTTPServer(directory=args.directory)
    server.start()
