FROM tomcat:7
RUN apt-get update
RUN apt-get install -y ansible
ADD ./ansible_tree /usr/local/share/ansible_tree
RUN ls -R /usr/local/share/ansible_tree
RUN ansible-playbook -i /usr/local/share/ansible_tree/hosts /usr/local/share/ansible_tree/site.yml --connection=local
CMD ["catalina.sh","run"]
