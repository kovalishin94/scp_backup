import configparser
from server import Server

# Read ini file
def read_settings(file: str) -> list[Server]:
    settings = configparser.ConfigParser()
    settings.read(file)
    print("Read settings...")
    server_list = []

    for section in settings.sections():
        section_dict = dict(settings.items(section))
        try:
            server = Server(**section_dict)
            server_list.append(server)
            print("Settings is correct!")
        except:
            print("Wrong arguments in settings.ini")

    print("We have fully and correct servers list!")
    return server_list

if __name__ == "__main__":
    server_list = read_settings("settings.ini")
    for server in server_list:
        try:
            ssh_client = server.create_ssh_client()
        except:
            print(f"Cannot connect to {server.host} by ssh")
            continue
        server.do_backup(ssh_client)
        ssh_client.close()
            
