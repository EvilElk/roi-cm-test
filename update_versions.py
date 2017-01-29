import sys
import yaml
import os
import xml.etree.ElementTree as xml
import logging


DEFAULT_CONFIG_PATH = './version-map.yml'
DEFAULT_PROJECTS_PATH = './'
POM_NAMESPACE_PREFIX = "{http://maven.apache.org/POM/4.0.0}"
POM_NAMESPACE_URI = "http://maven.apache.org/POM/4.0.0"


def get_version_map(confpath):
    with open(confpath, 'r') as conf_fp:
        return yaml.load(conf_fp)


def update_tag_text(tag, new_text):
    logging.info("Update {0}: {1} => {2}".format(tag.tag, tag.text, new_text))
    tag.text = new_text


def update_dependendecies(pom_tree, config):
    deps_list = pom_tree.findall("*"+POM_NAMESPACE_PREFIX+"dependency")
    for dependency in deps_list:
        #we need update version if dependency version scpecified and artifactId in config
        artifactId = dependency.find(POM_NAMESPACE_PREFIX+"artifactId")
        version = dependency.find(POM_NAMESPACE_PREFIX+"version")
        if (version is not None and artifactId is not None) and artifactId.text in config \
            and not version.text == config[artifactId.text]:
            logging.info("Update dependency: "+artifactId.text) 
            update_tag_text(version, config[artifactId.text])


def update_pom(pom_path, version_map):
    xml.register_namespace("", POM_NAMESPACE_URI)
    try:
      tree = xml.parse(pom_path)
    except Exception as e:
      logging.warn("Error while parsing {0}:{1}".format(pom_path,e))
      return

    project_name = tree.find("./"+POM_NAMESPACE_PREFIX+"artifactId").text
    if project_name in version_map:
        project_version_element = tree.find("./"+POM_NAMESPACE_PREFIX+"version")
        if not project_version_element.text == version_map[project_name]:
            logging.info("Update version for {0}".format(project_name))
            update_tag_text(project_version_element, version_map[project_name])
        
        #assume there is no need to update dependencies for not listed projects
        update_dependendecies(tree, version_map)
        #write resulted pom:
        tree.write(pom_path)
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    #TODO: use optparse 
    if len(sys.argv) < 2 :
        config_path = DEFAULT_CONFIG_PATH
    else:
        config_path = DEFAULT_CONFIG_PATH
    projects_path = DEFAULT_PROJECTS_PATH
    
    version_map = get_version_map(config_path)
    root_items = os.listdir(projects_path)
    #create list of all pom files in projects_path subdirs 
    project_poms = []
    for item in root_items:
        directory_path = projects_path+"/"+item
        if os.path.isdir(directory_path) and os.path.isfile(directory_path+"/pom.xml"):
            project_poms.append(directory_path+"/pom.xml")
    for i in  project_poms :
        update_pom(i, version_map) 
