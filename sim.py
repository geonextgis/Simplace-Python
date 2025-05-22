import simplace
import ipdb
import sys

# Define directories
install_dir = r'simplace_portable/workspace/'
work_dir = r'simulation-optuna/'
output_dir = r'simulation-optuna/output/'

# Initialize Simplace
sp = simplace.initSimplace(install_dir, work_dir, output_dir,
    javaParameters=[
        "-Xmx4g",
        "-Xms512m",
        "-XX:+UseG1GC",
        "-XX:+ExplicitGCInvokesConcurrent"
    ]
)

# Specify solution file
solution_file = r'simulation-optuna/SimulationExperimentTemplateTest/solution/Soil3_Germany_AllKreis_Test.sol.xml'
project_file = r'simulation-optuna/SimulationExperimentTemplateTest/project/Soil3_Germany_AllKreis.proj.xml'

simplace.openProject(sp, solution_file, project_file)
simplace.runProject(sp)
# simplace.closeProject(sp)

sp.shutDown()
import jpype
jpype.java.lang.System.exit(0)