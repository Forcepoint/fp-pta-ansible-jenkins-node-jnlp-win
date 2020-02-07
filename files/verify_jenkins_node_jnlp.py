"""
Author: Jeremy Cornett
Date: 2017-09-26
Purpose: Verify that the Jenkins node is actually connected.
"""

import argparse
import jenkins


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="Verify that the named node is connected to the Jenkins master.")
    parser.add_argument("url", help="The URL of the Jenkins master.")
    parser.add_argument("username", help="The name of a user on the Jenkins instance.")
    parser.add_argument("password", help="The user's password.")
    parser.add_argument("name", help="The intended name of the node.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Display additional information. Do not set this "
                                                                     "flag via ansible as the extra output will break "
                                                                     "the secret extraction.")
    args = parser.parse_args()

    # Connect to the Jenkins server.
    server = jenkins.Jenkins(args.url, username=args.username, password=args.password)

    # Verify that the node exists.
    if not server.node_exists(args.name):
        raise ValueError("A node with the specified name ({}) does not exist.".format(args.name))

    # Verify that it's connected.
    json_node_info = server.get_node_info(args.name)
    if json_node_info["offline"]:
        raise Exception("The node '{}' is offline.".format(args.name))
