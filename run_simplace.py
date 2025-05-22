import simplace
import jpype

def main():
    sp = simplace.initSimplace(r'simplace_portable/workspace/', r'simulation-optuna/', r'simulation-optuna/output/',
        javaParameters=[
            "-Xmx4g", "-Xms512m", "-XX:+UseG1GC", "-XX:+ExplicitGCInvokesConcurrent"
        ]
    )

    simplace.openProject(sp,
        solution='simulation-optuna/SimulationExperimentTemplateTest/solution/Soil3_Germany_AllKreis_Test.sol.xml',
        project='simulation-optuna/SimulationExperimentTemplateTest/project/Soil3_Germany_AllKreis.proj.xml'
    )
    simplace.runProject(sp)
    sp.shutDown()
    jpype.java.lang.System.exit(0)

if __name__ == "__main__":
    main()
