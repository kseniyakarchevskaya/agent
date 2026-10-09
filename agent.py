import socket
import threading
import sys
import toml 

def receive_messages(sock):
    """Поток для приема сообщений от сервера."""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\n[Соединение с брокером разорвано]")
                sys.exit(0)
            
            print(f"\r{data.decode('utf-8').strip()}")
            print("> ", end="", flush=True)
        except:
            break

def main():
    try:
        config = toml.load("agent.toml")
    except Exception as e:
        print(f"Ошибка чтения agent.toml: {e}")
        return

    host = config.get("broker_host", "127.0.0.1")
    port = config.get("broker_port", 4200)
    aid = config.get("agent_id", "terminal-1")
    name = config.get("display_name", "User")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except Exception as e:
        print(f"Не удалось подключиться к брокеру {host}:{port} — {e}")
        return

   
    sock.sendall(f"AUTH {aid} {name}\n".encode('utf-8'))
    auth_res = sock.recv(1024).decode('utf-8').strip()
    
    if auth_res != "AUTH_OK":
        print("Ошибка авторизации на брокере.")
        return
        
    print(f"Успешно подключено к брокеру! Ваше имя: {name}")
    print("Доступные команды: /list, /wait, /connect <id>, /leave, /quit")

   
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    
    while True:
        try:
            msg = input("> ").strip()
            if not msg: continue
            if msg == "/quit":
                break
            sock.sendall(f"{msg}\n".encode('utf-8'))
        except (KeyboardInterrupt, EOFError):
            break

    sock.close()
    print("\nОтключено.")

if __name__ == "__main__":
    main()
