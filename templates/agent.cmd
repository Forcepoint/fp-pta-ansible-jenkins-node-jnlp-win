java -jar {{ jenkins_node_path }}\agent.jar -jnlpUrl {{ jenkins_node_master_url }}/computer/{{ jenkins_node_name }}/slave-agent.jnlp -secret {{ jenkins_node_secret }} -workDir "{{ jenkins_node_path }}"

set agenExitCode=%errorlevel%

(echo %date% %time% jenkins agent exit && echo exit code %agenExitCode%) 1>> agent-%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1

exit /B %agenExitCode%