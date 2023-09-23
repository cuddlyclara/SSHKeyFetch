#!/usr/bin/python3

import requests
import sys
import os
import yaml

def get_github_keys(username, token):
    # Build the GitHub API URL for fetching user keys
    url = f'https://api.github.com/users/{username}/keys'

    # Set the necessary headers with the GitHub token
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

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
    
    # Check if both 'username' and 'token' are present in the configuration
    if not all(key in config for key in ('username', 'token')):
        raise ValueError('Username or token not set in config file')
    
    return config

def main(username):
    # Path for the cache file
    cachefilepath = os.path.expanduser(f'~{username}/.ssh/authorized_keys_github')

    try:
        # Get the configuration, obtain user keys, and store them in the cache.
        config = get_configuration(username)
        keys = get_github_keys(config['username'], config['token'])
        write_cachefile(keys, cachefilepath)
    except Exception as e:
        # If there's an exception, print the error message and try to read keys from the cache file
        print(e, file=sys.stderr)
        try:
            keys = read_cachefile(cachefilepath)
        except Exception:
            # If cachefile is not readable, use an empty list
            print(e, file=sys.stderr)
            keys = []
    
    write_console(keys)

if __name__ == "__main__":
    # Verify if the username has been specified as a command-line argument
    if len(sys.argv) != 2:
        sys.exit(1)

    # Get the username from the command-line argument and call the main function
    username = sys.argv[1]
    main(username)
