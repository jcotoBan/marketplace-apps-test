import requests
import sys
import socket
import time
from paramiko import SSHClient
from paramiko import MissingHostKeyPolicy
from paramiko import RSAKey
from halo import Halo
from Crypto.PublicKey import RSA

spinner = Halo(spinner='dots', text_color='cyan')

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

class mcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def display_regions():
    print('\n')
    response = requests.get("https://api.linode.com/v4/regions")
    if response.status_code == 200:
        data = response.json()
        regions = [(region['id'], region['label']) for region in data['data']]
        for region_id, region_label in regions:
            print(f"{region_id}: {region_label}")
    else:
        print(f"Failed to retrieve region data. Status code: {response.json()}")
    print('\n')

def ssh_validator(host):

    spinner.start(text='checking connection on port 22')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host,22))
    while result != 0:
        result = sock.connect_ex((host,22))
        time.sleep(10)

    sock.close()
    spinner.stop()

    print(f"{mcolors.OKGREEN}port 22 is open\n{mcolors.ENDC}", end='') 

def ansible_process_validator(host):
    ssh_user = "root"
    key = "/tmp/testkey"
    ssh_port = 22
    client = SSHClient()
    client.set_missing_host_key_policy(MissingHostKeyPolicy())
    client.connect(host, port=ssh_port, username=ssh_user, key_filename=key)
    stdin, stdout, stderr = client.exec_command("pgrep -f ansible-playbook")

    spinner.start(text='Waiting ansible playbook to start')
    while not stdout.readlines() :
        time.sleep(10) 
        stdin, stdout, stderr = client.exec_command("pgrep -f ansible-playbook")
    spinner.stop()
    print(f"{mcolors.OKGREEN}ansible playbook started\n{mcolors.ENDC}", end='')

    #readlines reads in buffer, so stdout gets cleaned
    stdin, stdout, stderr = client.exec_command("pgrep -f ansible-playbook")
    
    spinner.start(text='Waiting ansible playbook to finish')
    while stdout.readlines() :
        time.sleep(10)
        stdin, stdout, stderr = client.exec_command("pgrep -f ansible-playbook")
    spinner.stop()
    print(f"{mcolors.OKGREEN}ansible playbook stopped\n\n{mcolors.ENDC}", end='')

    if client:
        client.close()

def print_ansible_recap(host):
    ssh_user = "root"
    key = "/tmp/testkey"
    ssh_port = 22
    client = SSHClient()
    client.set_missing_host_key_policy(MissingHostKeyPolicy())
    client.connect(host, port=ssh_port, username=ssh_user, key_filename=key)
    stdin, stdout, stderr = client.exec_command("awk '/PLAY RECAP/{p=1}/^ *$/{p=0}p' /var/log/stackscript.log")
    print(*stdout.readlines())
    print('\n')

    if client:
        client.close()

def print_ansible_errors(host):

    ssh_user = "root"
    key = "/tmp/testkey"
    ssh_port = 22
    client = SSHClient()
    client.set_missing_host_key_policy(MissingHostKeyPolicy())
    client.connect(host, port=ssh_port, username=ssh_user, key_filename=key)
    stdin, stdout, stderr = client.exec_command("awk -v RS= '/FAILED/' /var/log/stackscript.log")
    output = stdout.readlines()
    if client:
       client.close()

    if output:
        print(f"{mcolors.FAIL}Ansible tasks with errors{mcolors.ENDC}\n", end='')
        print(*output)
        print('\n')

def curl_wordpress_rdns_domain(token, region, email, root_pass, authorized_user):
   
    api_url = "https://api.linode.com/v4/linode/instances"

    payload = {
        "authorized_users": [authorized_user],
        "backups_enabled": False,
        "booted": True,
        "image": "linode/ubuntu22.04",
        "label": "wordpress_rdns_test",
        "private_ip": False,
        "region": region,
        "root_pass": root_pass,
        "stackscript_data": {
            "disable_root": "No",
            "soa_email_address": email,
            "webserver_stack": "LAMP",
            "site_title": "test_blog",
            "wp_admin_user": "admin",
            "wp_db_user": "admindb",
            "wp_db_name": "dbwp",
            "user_name": "jucot"
        },
        "stackscript_id": 401697,
        "tags": [],
        "type": "g6-standard-4"
    }

    response = requests.post(api_url, json=payload, auth=BearerAuth(token))

    if response.status_code == 200:
        print("Linode instance created successfully.\n\n")
        return response
    else:
        print(f"{mcolors.FAIL}Failed to deploy instance. {response.json()} {mcolors.ENDC}")
        sys.exit()

def curl_wordpress_custom_domain(token, region, email, root_pass, authorized_user):
   
    api_url = "https://api.linode.com/v4/linode/instances"

    payload = {
        "authorized_users": [authorized_user],
        "backups_enabled": False,
        "booted": True,
        "image": "linode/ubuntu22.04",
        "label": "wordpress_custom_test",
        "private_ip": False,
        "region": region,
        "root_pass": root_pass,
        "stackscript_data": {
            "disable_root": "No",
            "soa_email_address": email,
            "webserver_stack": "LAMP",
            "site_title": "test_blog",
            "wp_admin_user": "admin",
            "wp_db_user": "admindb",
            "wp_db_name": "dbwp",
            "user_name": "jucot",
            "password": root_pass,
            "domain": "jccsutils.net", 
            "token_password": token,
            "subdomain": "www",
        },
        "stackscript_id": 401697,
        "tags": [],
        "type": "g6-standard-4"
    }

    response = requests.post(api_url, json=payload, auth=BearerAuth(token))

    if response.status_code == 200:
        print("Linode instance created successfully.\n\n")
        return response
    else:
        print(f"{mcolors.FAIL}Failed to deploy instance. {response.json()} {mcolors.ENDC}")
        sys.exit()

def curl_nomad(token, region, email, root_pass, authorized_user):
   
    api_url = "https://api.linode.com/v4/linode/instances"

    payload = {
        "authorized_users": [authorized_user],
        "backups_enabled": False,
        "booted": True,
        "image": "linode/ubuntu22.04",
        "label": "nomad_custom_test",
        "private_ip": False,
        "region": region,
        "root_pass": root_pass,
        "stackscript_data": {
           "clusterheader": "Yes",
            "add_ssh_keys": "no",
            "cluster_size": "6",
            "servers": "3",
            "clients": "3",
            "token_password": token,
            "sudo_username": "test_sudo",
            "email_address": email
        },
        "stackscript_id": 1226544,
        "tags": [],
        "type": "g6-standard-4"
    }

    response = requests.post(api_url, json=payload, auth=BearerAuth(token))

    if response.status_code == 200:
        print("Linode instance created successfully.\n\n")
        return response
    else:
        print(f"{mcolors.FAIL}Failed to deploy instance. {response.json()} {mcolors.ENDC}")
        sys.exit()

def create_sshkeypair():
    key = RSA.generate(1024)
    f = open("/tmp/testkey", "wb")
    f.write(key.exportKey('PEM'))
    f.close()

    pubkey = key.publickey()
    f = open("/tmp/testkey.pub", "wb")
    f.write(pubkey.exportKey('OpenSSH'))
    f.close()
    return pubkey.exportKey('OpenSSH').decode()
   
def create_key_cloudman(token,sshkey): 

    api_url = "https://api.linode.com/v4/profile/sshkeys"

    payload = {
        "label": "tmpkey",
        "ssh_key": sshkey
    }

    response = requests.post(api_url, json=payload, auth=BearerAuth(token))

    if response.status_code == 200:
        print("Temporary keys have been added to your Linode Account.\n\n")
        return response
    else:
        print(f"{mcolors.FAIL}Failed to generate keys. {response.json()} {mcolors.ENDC}")
        sys.exit()

def delete_key_cloudman(token,sshkey_id):
   
    url = f"https://api.linode.com/v4/profile/sshkeys/{sshkey_id}"

    response = requests.delete(url, auth=BearerAuth(token))

    if response.status_code == 200:
        print("SSH key successfully deleted from cloud manager.")
    else:
        print(f"Failed to delete SSH key. Status code: {response.status_code}")
        print(response.text)

def delete_instance(token, instance_id):

    url = f"https://api.linode.com/v4/linode/instances/{instance_id}"
    response = requests.delete(url, auth=BearerAuth(token))

    if response.status_code == 200:
        print(f"Linode {instance_id} successfully deleted  from cloud manager.")
    else:
        print(f"Failed to delete Linode. Status code: {response.status_code}")
        print(response.text)

def delete_nomad_cluster_instance(token):

    linodes=''
    url = "https://api.linode.com/v4/linode/instances"
    response = requests.get(url, auth=BearerAuth(token))
    
    if response.status_code == 200:
        linodes=response.json()
    else:
        print(f"Failed to get linodes. Status code: {response.status_code}")
        print(response.json())
        
    filtered_objects = [obj for obj in linodes['data'] if 'nomad_custom_test' in obj['label']]

    for obj in filtered_objects:
        delete_instance(token,obj['id'])

def delete_custom_domain(token):

    domains=''
    urlget = "https://api.linode.com/v4/domains"
    response = requests.get(urlget, auth=BearerAuth(token))
    
    if response.status_code == 200:
        domains=response.json()
    else:
        print(f"Failed to get domains. Status code: {response.status_code}")
        print(response.json())

    index = next((i for i, obj in enumerate(domains['data']) if obj['domain'] == "jccsutils.net"), None)

    urldelete = f"https://api.linode.com/v4/domains/{domains['data'][index]['id']}"

    response = requests.delete(urldelete, auth=BearerAuth(token))
        
    if response.status_code == 200:
        print("Custom domain successfully deleted  from cloud manager.")
    else:
        print(f"Failed to delete Domain. Status code: {response.status_code}")
        print(response.json())



