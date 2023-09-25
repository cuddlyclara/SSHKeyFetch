#!/usr/bin/python3

"""
Name: cuddlyclara
Website: cuddlyclara.de
Source: https://github.com/cuddlyclara/SSHKeyFetch
Description: This program uses SSH keys stored in GitHub for secure client authentication with OpenSSH servers via the "AuthorizedKeysCommand" option.
"""

import requests
import sys
import os
import yaml
import time
from timeout_decorator import timeout

# Set Timeout
@timeout(10)
def get_github_keys(username, token=None):
    # Build the GitHub API URL for fetching user keys
    url = f'https://api.github.com/users/{username}/keys'

    # Define the base headers
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }

    # Add an optional token to the headers if provided
    if token is not None:
        headers['Authorization'] = f'token {token}'

    # Send a GET request to fetch user keys
    response = requests.get(url, headers=headers, timeout=5)

    # Check if the response status code is not 200 (OK)
    if response.status_code != 200:
        raise ValueError('Bad return code')

    # Extract and return the user keys
    return [key['key'] for key in response.json()]

def write_cachefile(keys, path):
    # Write keys to the cache file
    with open(path, 'w') as cachefile:
        for key in keys:
            cachefile.write(key + '\n')

def read_cachefile(path):
    # Read keys from the cache file
    with open(path, 'r') as cachefile:
        keys = [key.strip() for key in cachefile.readlines()]
    return keys

def check_cachefile_changed_recently(path, threshold_seconds=10):
    if os.path.exists(path):
        file_modified_time = os.path.getmtime(path)
        current_time = time.time()
        return current_time - file_modified_time <= threshold_seconds
    return False

def write_console(keys):
    # Print the keys to the console via stdout
    for key in keys:
        print(key)

def get_configuration(username):
    # Get the path to the user's configuration file
    config_file_path = os.path.expanduser(f'~{username}/.ssh/github.yaml')

    # Read the configuration from YAML file
    with open(config_file_path, 'r') as configuration_file:
        config = yaml.safe_load(configuration_file)

    # Check if 'username' is present in the configuration file
    if 'username' not in config:
        raise ValueError('Username not set in config file')
    return config

def main(username):
    # Path for the cache file
    cachefilepath = os.path.expanduser(f'~{username}/.ssh/authorized_keys_github')

    # Try to load the configuration file
    try:
        config = get_configuration(username)
    except Exception as e:
        # If configuration is not readable, print the error message to stderr and exit with code 1
        print(e, file=sys.stderr)
        exit(1)

    try:
        if check_cachefile_changed_recently(cachefilepath):
            # If the cache file has been recently updated, retrieve keys from it to reduce the number of requests to GitHub
            keys = read_cachefile(cachefilepath)
        else:
            try:
                # Otherwise, obtain keys from GitHub and store them in the cache
                keys = get_github_keys(config.get('username'), config.get('token'))
                write_cachefile(keys, cachefilepath)
            except Exception as e:
                # If there's an exception while accessing GitHub, print the error message and try to read keys from the cache file
                print(e, file=sys.stderr)
                keys = read_cachefile(cachefilepath)
    except Exception as e:
        # If cachefile is not readable, print the error message and use an empty key list
        print(e, file=sys.stderr)
        keys = []

    write_console(keys)

if __name__ == '__main__':
    # Verify if the username has been specified as a command-line argument
    if len(sys.argv) != 2:
        sys.exit(1)

    # Get the username from the command-line argument
    username = sys.argv[1]

    # Call the main function
    try:
        main(username)
    except Exception as e:
        print(e, file=sys.stderr)
        exit(1)
