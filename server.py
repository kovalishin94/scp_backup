import os
import datetime
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

class Server:
    def __init__(
            self, 
            host: str, 
            port: int, 
            user: str, 
            backup_target: str, 
            local_path: str, 
            password: str = None, 
            key_file_path: str = None, 
            passphrase: str = None) -> None:
        
        self.host = host
        self.port = port
        self.user = user
        self.backup_target = backup_target
        self.local_path = local_path
        self.password = password
        self.key_file_path = key_file_path
        self.passphrase = passphrase

    # Create SSH client
    def create_ssh_client(self) -> SSHClient:
        ssh_client = SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        
        ssh_settings = {
            "hostname": self.host,
            "port": self.port,
            "username": self.user
        }

        if self.key_file_path:
            ssh_settings["key_filename"] = self.key_file_path
            ssh_settings["passphrase"] = self.passphrase
        else:
            # load_dotenv()
            key = os.getenv("KEY_FERNET")
            cipher_suite = Fernet(key)
            ssh_settings["password"] = cipher_suite.decrypt(self.password)

        try:
            ssh_client.connect(**ssh_settings)
        except:
            print(f"Cannot connect to {self.host}")

        return ssh_client

    # Download file by SCP
    def scp_download(self, ssh_client: SSHClient, remote_path: str):
        with SCPClient(ssh_client.get_transport()) as scp:
            scp.get(remote_path, self.local_path)

    # Do backup
    def do_backup(self, ssh_client: SSHClient):
        dirname = os.path.basename(self.backup_target)
        parent_dir = os.path.dirname(self.backup_target)
        backup_name = parent_dir + \
                        f"/{dirname}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.zip"
        print(f"Doing backup {self.host} ...")
        command = f"cd {self.backup_target} && zip -r {backup_name} ./*"
        try:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            print(stdout.read().decode())
        except:
            print("Something going wrong ...")
        
        try:
            self.scp_download(ssh_client, backup_name)
            print(f"Backup {self.host} was succesfully downloaded!")
        except:
            print(f"Cannot download backup {self.host}")
        
        try:
            stdin, stdout, stderr = ssh_client.exec_command(f"rm {backup_name}")
        except:
            print("Something going wrong ...")