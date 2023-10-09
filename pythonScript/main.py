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

print(f"{mcolors.OKBLUE}>>>>>>>>>>>> Launching Test Deploys <<<<<<<<<<<<\n{mcolors.ENDC}", end='')

output_wrdns=curl_wordpress_rdns_domain(token, region, email, root_pass, authorized_user)
output_wcustom=curl_wordpress_custom_domain(token, region, email, root_pass, authorized_user)
output_nomad=curl_nomad(token, region, email, root_pass, authorized_user)

wrnds_host = output_wrdns.json().get('ipv4', [])[0]
wrnds_id = output_wrdns.json().get('id', None)

wcustom_host = output_wcustom.json().get('ipv4', [])[0]
wcustom_id = output_wcustom.json().get('id', None)

nomad_host = output_nomad.json().get('ipv4', [])[0]
nomad_id = output_nomad.json().get('id', None)


print(f"{mcolors.OKBLUE}Ansible Playbook Verification\n{mcolors.ENDC}", end='')
ssh_validator(wrnds_host)
ssh_validator(wcustom_host)
ssh_validator(nomad_host)

ansible_process_validator(wrnds_host)
print(f"{mcolors.OKBLUE}Ansible Recaps{mcolors.ENDC}\n", end='')
print(f"{mcolors.OKBLUE}Wordpress default domain: {mcolors.ENDC}\n", end='')
print_ansible_recap(wrnds_host)
print_ansible_errors(wrnds_host)

ansible_process_validator(wcustom_host)
print(f"{mcolors.OKBLUE}Wordpress custom domain: {mcolors.ENDC}\n", end='')
print_ansible_recap(wcustom_host)
print_ansible_errors(wcustom_host)

ansible_process_validator(nomad_host)
print(f"{mcolors.OKBLUE}Nomad cluster default domain: {mcolors.ENDC}\n", end='')
print_ansible_recap(nomad_host)
print_ansible_errors(nomad_host)


print('')

delete_instance(token, wrnds_id)
delete_instance(token, wcustom_id)
delete_instance(token, nomad_id)
delete_nomad_cluster_instance(token)
delete_key_cloudman(token, key_id)
delete_custom_domain(token)
