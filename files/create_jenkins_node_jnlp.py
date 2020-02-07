"""
Author: Jeremy Cornett
Date: 2018-01-19
Purpose: Create/reconfigure a Jenkins JNLP agent node.
"""

import argparse
import jenkins
import os
from xml.etree import ElementTree


def set_element_text(tree, tag, text):
    """Set the text of an XML tag in the given XML tree. Create the tag if it doesn't exist.
    :param tree: The XML tree.
    :type tree: xml.etree.ElementTree
    :param tag: The name of the element tag to search for.
    :type tag: str
    :param text: The text to place in the element.
    :type text: str
    :return: None
    """
    element = tree.find(tag)
    if element is None:
        if "/" in tag:
            raise Exception("Tag '{}' is too complex for this script to handle.".format(tag))
        else:
            element = ElementTree.SubElement(tree, tag)
    element.text = text


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="Create/Reconfig a node on a Jenkins master. This does NOT support "
                                                 "renaming of nodes or deleting nodes. This simply looks for a node "
                                                 "name. If it exists, update it's info. If it doesn't exist, "
                                                 "create it. Prints the JNLP secret for connecting.")
    parser.add_argument("url", help="The URL of the Jenkins master.")
    parser.add_argument("username", help="The name of a user on the Jenkins instance.")
    parser.add_argument("password", help="The user's password.")
    parser.add_argument("name", help="The intended name of the node.")
    parser.add_argument("description", help="The description of the node.")
    parser.add_argument("labels", help="The labels to apply to the node, which is used for determining where to run "
                                       "jobs.")
    parser.add_argument("path_secret", help="Path to the file to store the node secret in.")
    parser.add_argument("-n", "--num-executors", default="1", help="")
    parser.add_argument("-f", "--force", action="store_true", help="Force the deletion and full recreation of "
                                                                   "the node.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Display additional information. Do not set this "
                                                                     "flag via ansible as the extra output will break "
                                                                     "the secret extraction.")
    parser.add_argument("-p", "--path", default="/jenkins",
                        help="The default path Jenkins will use on the node for the workspace and associated files.")
    parser.add_argument("-m", "--mode", default="EXCLUSIVE", help="The mode in which to connect the node to the "
                                                                  "master.")
    args = parser.parse_args()

    # Connect to the Jenkins server.
    server = jenkins.Jenkins(args.url, username=args.username, password=args.password)

    # Delete the node if required.
    if args.force and server.node_exists(args.name):
        server.delete_node(args.name)
        if args.verbose:
            print("Force delete of node {}.".format(args.name))
            print()

    # If the node doesn't already exist, create it.
    if not server.node_exists(args.name):
        server.create_node(
            args.name,
            nodeDescription=args.description,
            numExecutors=args.num_executors,
            remoteFS=args.path,
            labels=args.labels,
            exclusive=(args.mode == "EXCLUSIVE"),
            launcher=jenkins.LAUNCHER_JNLP)
    else:
        # The node does already exist. Get its config, and change what's needed.

        # We can assume the node exists, but we cannot assume it is already configured correctly.
        str_xml_node_config = server.get_node_config(args.name)
        if args.verbose:
            print("BEFORE MOD")
            print("----------")
            print(str_xml_node_config)
            print()

        ''' EXAMPLE CONFIG JNLP Agent
        <?xml version="1.0" encoding="UTF-8"?>
        <slave>
          <name>Test01</name>
          <description></description>
          <remoteFS>/jenkins</remoteFS>
          <numExecutors>1</numExecutors>
          <mode>EXCLUSIVE</mode>
          <retentionStrategy class="hudson.slaves.RetentionStrategy$Always"/>
          <launcher class="hudson.slaves.JNLPLauncher">
            <workDirSettings>
              <disabled>false</disabled>
              <internalDir>remoting</internalDir>
              <failIfWorkDirIsMissing>false</failIfWorkDirIsMissing>
            </workDirSettings>
          </launcher>
          <label>Test01</label>
          <nodeProperties/>
        </slave>
        '''

        # Load the node's config into an xml tree for ease of manipulation.
        tree_node_config = ElementTree.fromstring(str_xml_node_config)

        # Set all the original data again.
        set_element_text(tree_node_config, "description", args.description)
        set_element_text(tree_node_config, "remoteFS", args.path)
        set_element_text(tree_node_config, "numExecutors", args.num_executors)
        set_element_text(tree_node_config, "mode", args.mode)
        set_element_text(tree_node_config, "label", args.labels)

        # Double check that the changes were made.
        # For whatever reason the tostring function returns a binary string.
        str_xml_node_config_mod = ElementTree.tostring(tree_node_config).decode('ascii')
        if args.verbose:
            print("AFTER MOD")
            print("----------")
            print(str_xml_node_config_mod)
            print()

        # Reconfig the node.
        server.reconfig_node(args.name, str_xml_node_config_mod)

    # Run a script to get the node's secret.
    # https://support.cloudbees.com/hc/en-us/articles/222520647-How-to-find-slave-secret-key-
    node_secret = server.run_script("for (aSlave in hudson.model.Hudson.instance.slaves) "
                                   "{ if (aSlave.name == '" + args.name +
                                   "') { println aSlave.getComputer().getJnlpMac() } }")

    # Save the secret so ansible can access it. This lets ansible trigger a reset if the secret has changed.
    with open(os.path.abspath(args.path_secret), "w") as file_node_secret:
        file_node_secret.write(node_secret)
