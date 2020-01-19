#!/usr/bin/env python

import argparse
import os
import time

import googleapiclient.discovery
from six.moves import input

import json


def _get_path(filename):
    return os.path.join(CURRENT_FOLDER, filename)


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../config/config.json"
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(_get_path('../config'), 'config.json')

with open('../config/config.json', 'r') as JSON:
    json_dict = json.load(JSON)
print(json_dict["eth_param"]['nodeNumber'])
print(json_dict["project_id"])


# [START list_instances]

def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None


# [END list_instances]

# [START create_instance]
def create_instance(compute, project, zone, name):
    # Get the latest Debian Jessie image.
    image_response = compute.images().getFromFamily(
        project='ubuntu-os-cloud', family='ubuntu-1804-lts').execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup-script.sh'), 'r').read()

    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        "tags": {
            "items": [
                "http-server",
                "https-server"
            ]},

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }, {
            },  # {
            ]
        }
    }

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()


# [END create_instance]


# [START wait_for_operation]
def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)


# [END wait_for_operation]


# [START run]
def main(project, zone, instance_name, wait=True):
    compute = googleapiclient.discovery.build('compute', 'v1')

    print('Creating instance.')

    for i in range(1, 1 + (json_dict["eth_param"]['nodeNumber'])):
        operation = create_instance(compute, project, zone, instance_name + str(i))
        wait_for_operation(compute, project, zone, operation['name'])

    instances = list_instances(compute, project, zone)

    print('Instances in project %s and zone %s:' % (project, zone))
    for instance in instances:
        print(' - ' + instance['name'])

    print("""
Instance created.
It will take a minute or two for the instance to complete work.
""".format())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--project_id', default=(json_dict["project_id"]), help='Your Google Cloud project ID.')
    parser.add_argument('--zone', default='europe-west1-b', help='Compute Engine zone to deploy to.')
    parser.add_argument('--name', default='ethereum', help='New instance name.')
    args = parser.parse_args()
    main(args.project_id, args.zone, args.name)
# [END run]
