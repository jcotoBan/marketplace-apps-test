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

print(f"{mcolors.OKBLUE}Authorized user for ssh_keys : {mcolors.ENDC}", end='')
authorized_user = input()

root_pass="4dsf*asdf4as*"


os.system('clear')

#Creating and uploading temp key for testing

key_id=create_key_cloudman(token, create_sshkeypair()).json().get('id', None)

#wordpress rnds_domain

print(f"{mcolors.OKBLUE}>>>>>>>>>>>> Wordpress rdns domain <<<<<<<<<<<<\n{mcolors.ENDC}", end='')

output=curl_wordpress_rdns_domain(token, region, email, root_pass, authorized_user)

if output != 200:
    delete_key_cloudman(token, key_id)
    sys.exit()

wrnds_host = output.json().get('ipv4', [])[0]
wrnds_id = output.json().get('id', None)


print(f"{mcolors.OKBLUE}Ansible Playbook Verification\n{mcolors.ENDC}", end='')
ssh_validator(wrnds_host)
ansible_process_validator(wrnds_host)

print(f"{mcolors.OKBLUE}Ansible Recaps{mcolors.ENDC}\n", end='')
print_ansible_recap(wrnds_host)
print_ansible_errors(wrnds_host)

delete_instance(token,wrnds_id)

print('')

#wordpress custom_domain

print(f"{mcolors.OKBLUE}>>>>>>>>>>>> Wordpress custom domain <<<<<<<<<<<<\n{mcolors.ENDC}", end='')

output=curl_wordpress_custom_domain(token, region, email, root_pass, authorized_user)

if output != 200:
    delete_instance(token,wrnds_id)
    delete_key_cloudman(token, key_id)
    sys.exit()

w_custom_host = output.json().get('ipv4', [])[0]
w_custom_id = output.json().get('id', None)

print(f"{mcolors.OKBLUE}Ansible Playbook Verification\n{mcolors.ENDC}", end='')
ssh_validator(w_custom_host)
ansible_process_validator(w_custom_host)

print(f"{mcolors.OKBLUE}Ansible Recaps{mcolors.ENDC}\n", end='')
print_ansible_recap(w_custom_host)
print_ansible_errors(w_custom_host)

delete_instance(token,w_custom_id)

print('')

#nomad test

print(f"{mcolors.OKBLUE}>>>>>>>>>>>> Nomad custom domain <<<<<<<<<<<<\n{mcolors.ENDC}", end='')

output=curl_nomad(token, region, email, root_pass, authorized_user)


if output != 200:
    delete_instance(token,wrnds_id)
    delete_instance(token,w_custom_id)
    delete_custom_domain(token)
    delete_key_cloudman(token, key_id)
    sys.exit()


nomad_host = output.json().get('ipv4', [])[0]

print(f"{mcolors.OKBLUE}Ansible Playbook Verification\n{mcolors.ENDC}", end='')
ssh_validator(nomad_host)
ansible_process_validator(nomad_host)

print(f"{mcolors.OKBLUE}Ansible Recaps{mcolors.ENDC}\n", end='')
print_ansible_recap(nomad_host)
print_ansible_errors(nomad_host)


delete_nomad_cluster_instance(token)
delete_key_cloudman(token, key_id)
delete_custom_domain(token)
