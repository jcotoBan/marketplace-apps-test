import json
import os

from helpers import *

print(f"\n{mcolors.OKBLUE}Enter your Linode API token: {mcolors.ENDC}", end='')
token = input()

display_regions()
print(f"{mcolors.OKBLUE}Enter the region id region where you will run the tests: {mcolors.ENDC}", end='')
region = input()

print(f"{mcolors.OKBLUE}Enter an email address for the notifications and SOA of domain: {mcolors.ENDC}", end='')
email = input()

os.system('clear')

#Creating and uploading temp key for testing

key_id=create_key_cloudman(token, create_sshkeypair()).json().get('id', None)

#wordpress rnds_domain

print(f"{mcolors.OKBLUE}>>>>>>>>>>>> Wordpress rdns domain <<<<<<<<<<<<\n{mcolors.ENDC}", end='')

output=curl_wordpress_rdns_domain(token, region, email, "4dsf*asdf4as*").json()
host = output.get('ipv4', [])[0]
id = output.get('id', None)

print(f"{mcolors.OKBLUE}Ansible Playbook Verification\n{mcolors.ENDC}", end='')
ssh_validator(host)
ansible_process_validator(host)

print(f"{mcolors.OKBLUE}Ansible Recaps{mcolors.ENDC}\n", end='')
print_ansible_recap(host)
print_ansible_errors(host)

delete_instance(token,id)

#wordpress custom_domain

print(f"{mcolors.OKBLUE}>>>>>>>>>>>> Wordpress custom domain <<<<<<<<<<<<\n{mcolors.ENDC}", end='')

output=curl_wordpress_custom_domain(token, region, email, "4dsf*asdf4as*").json()
host = output.get('ipv4', [])[0]
id = output.get('id', None)

print(f"{mcolors.OKBLUE}Ansible Playbook Verification\n{mcolors.ENDC}", end='')
ssh_validator(host)
ansible_process_validator(host)

print(f"{mcolors.OKBLUE}Ansible Recaps{mcolors.ENDC}\n", end='')
print_ansible_recap(host)
print_ansible_errors(host)

delete_instance(token,id)

#nomad test

print(f"{mcolors.OKBLUE}>>>>>>>>>>>> Nomad custom domain <<<<<<<<<<<<\n{mcolors.ENDC}", end='')

output=curl_nomad(token, region, email, "4dsf*asdf4as*").json()
host = output.get('ipv4', [])[0]

print(f"{mcolors.OKBLUE}Ansible Playbook Verification\n{mcolors.ENDC}", end='')
ssh_validator(host)
ansible_process_validator(host)

print(f"{mcolors.OKBLUE}Ansible Recaps{mcolors.ENDC}\n", end='')
print_ansible_recap(host)
print_ansible_errors(host)

delete_nomad_cluster_instance(token)
delete_key_cloudman(token, key_id)
delete_custom_domain(token)
