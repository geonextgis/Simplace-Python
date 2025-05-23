import simplace
import jpype
import yaml
import sys

def run_simplace(config_path: str):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    paths = config['simplace_paths']
    install_dir = paths['install_dir']
    work_dir = paths['work_dir']
    output_dir = paths['output_dir']
    solution_file = paths['solution_file']
    project_file = paths['project_file']
    
    print(paths)

    sp = simplace.initSimplace(
        install_dir, work_dir, output_dir,
        # javaParameters=[
        #     "-Xmx4g", "-Xms512m",
        #     "-XX:+UseG1GC", "-XX:+ExplicitGCInvokesConcurrent"
        # ]
    )

    simplace.openProject(sp, solution_file, project_file)
    simplace.runProject(sp)
    sp.shutDown()
    jpype.java.lang.System.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python simplace_run.py <config.yaml>")
        sys.exit(1)
    run_simplace(sys.argv[1])
