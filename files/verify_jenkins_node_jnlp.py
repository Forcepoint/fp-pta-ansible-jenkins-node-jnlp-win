"""
Author: Jeremy Cornett
Date: 2017-09-26
Purpose: Verify that the Jenkins node is actually connected.
"""

import argparse
import subprocess
import time

import jenkins


def verify_jenkins_node_jnlp(jenkins_url, jenkins_user, jenkins_password, node_name, task_name):
    """ Verify that the Jenkins node is actually connected.
    :param jenkins_url: The URL to the Jenkins master.
    :type jenkins_url: str
    :param jenkins_user: The username to connect with the Jenkins master.
    :type jenkins_user: str
    :param jenkins_password: The password to connect with the Jenkins master.
    :type jenkins_password: str
    :param node_name: The name of the node in question.
    :type node_name: str
    :param task_name: The task name which initiates the node's connection to the Jenkins master.
    :type task_name: str
    :return: None
    """
    # Connect to the Jenkins server.
    server = jenkins.Jenkins(jenkins_url, username=jenkins_user, password=jenkins_password)

    # Verify that the node exists.
    if not server.node_exists(node_name):
        raise ValueError("A node with the specified name ({}) does not exist.".format(args.name))

    # Verify that it's connected. Loop for a while to retry making the connection.
    retry_count = 0
    retry_interval = 60
    retry_max = 24*60    # Aiming for 24 hours.
    connected = False
    while not connected:
        retry_count += 1
        json_node_info = server.get_node_info(node_name)
        if json_node_info["offline"]:
            if retry_count == retry_max-1:
                raise Exception("The node '{}' is offline.".format(node_name))
            # Stop the scheduled task.
            subprocess.run(["SCHTASKS.EXE", "/End", "/TN", task_name], check=True, timeout=retry_interval)
            time.sleep(5)
            # Run the scheduled task again.
            subprocess.run(["SCHTASKS.EXE", "/Run", "/TN", task_name], check=True, timeout=retry_interval)
            time.sleep(retry_interval)
        else:
            connected = True


if __name__ == "__main__":
    # pylint: disable=invalid-name

    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="Verify that the named node is connected to the Jenkins master.")
    parser.add_argument("url", help="The URL of the Jenkins master.")
    parser.add_argument("username", help="The name of a user on the Jenkins instance.")
    parser.add_argument("password", help="The user's password.")
    parser.add_argument("name", help="The intended name of the node.")
    parser.add_argument("task_name", help="The name of the scheduled task responsible for making the connection to the"
                                          "Jenkins master.")
    args = parser.parse_args()

    verify_jenkins_node_jnlp(args.url, args.username, args.password, args.name, args.task_name)
