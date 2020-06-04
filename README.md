# jenkins-node-jnlp-win

Setup the Windows host as a Jenkins JNLP node, add the node's configuration to the master, 
configure the Windows user to start the connection to the master,
and then reboot if needed so the connection is initiated.

The JNLP connection is with latest version of OpenJDK 11.

This is NOT the preferred method of connecting to the Jenkins master as the master has no recourse for
reconnecting. The connection is initiated on the node. This role though, will setup a scheduled
task that will run under the Windows user and start the JNLP agent when Windows starts. 
This will give Jenkins jobs the ability to interact with the desktop.

This type of connection is necessary though if the jobs on this Jenkins node require a GUI to run, 
like UI testing or something else that interacts with the desktop.
SSH connections do not provide use of the desktop unfortunately.

## Requirements

The Jenkins master already exists and basic setup is complete. 
The Jenkins master is running OpenJDK 11 or higher.

## Role Variables

### REQUIRED
* jenkins_node_master_url: The URL to the Jenkins master this node will connect with.
* jenkins_node_master_user: A user on the Jenkins master that has enough permissions to add a node.
* jenkins_node_master_password: The password for the user on the Jenkins master. This should be vaulted.
* jenkins_node_user_name: The user name on Windows for creating JNLP connection with. 
  **This must be the same user the ansible connection is made with to your Windows machine.
  The user must already exist.**
* jenkins_node_user_password: The password for the user on Windows for creating the JNLP connection with.

Make sure you get those passwords vaulted so they're not in plain text!

### OPTIONAL
* jenkins_node_name: The name for the node. This defaults to the ansible host name.
* jenkins_node_description: The description for the node. The default is blank.
* jenkins_node_executors: The number of executors for the node. This defaults to 1.
* jenkins_node_labels: The labels to apply for the node. Multiple labels should be separated by a space. 
  This defaults to the ansible host name.
* jenkins_node_host: The DNS/IP address for the node. This defaults to the ansible host's default IPV4 address.
* jenkins_node_master_ca_cert: The path to the CA certificate for verifying SSL connections with the master, if needed.
* jenkins_node_openjdk_major_version: The major version of OpenJDK to install. This defaults to the same major version
  that the jenkins master role uses.
* jenkins_node_openjdk_full_version: The full version of OpenJDK to install. Defaults to "latest" but you can provide a
  specific version if you like. EX: "11.0.6.1"

## Dependencies

None

## Example Playbook

Again, make sure you get those passwords vaulted so they're not in plain text!

      hosts: jenkinsnode01
      vars:
        jenkins_node_master_address: https://jenkins.COMPANY.com
        jenkins_node_master_user: admin
        jenkins_node_master_password: Password1
        jenkins_node_user_name: Administrator
        jenkins_node_user_password: Password2
      roles:
        - role: jenkins-node-jnlp-win

## License

BSD-3-Clause

## Author Information

Jeremy Cornett <jeremy.cornett@forcepoint.com>
