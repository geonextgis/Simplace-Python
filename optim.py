from lxml import etree
import yaml
import numpy as np
import optuna
import subprocess
import logging
from logging.handlers import RotatingFileHandler
import warnings

warnings.filterwarnings('ignore')


class SimplaceOptimizer:
    def __init__(self, xml_path, config_path, process_result_fn, loss_fn, device='local', log_file=None):
        """
        Initializes the SimplaceOptimizer class.

        Parameters:
        -----------
        xml_path : str
            Path to the simulation XML file.
        config_path : str
            Path to the YAML configuration file.
        process_result_fn : callable
            Function to process simulation outputs.
        loss_fn : callable
            Function to compute the error/loss.
        log_file : str, optional
            Path to a log file. If provided, logs are written to file with rotation.
        """
        self.xml_path = xml_path
        self.config_path = config_path
        self.process_result_fn = process_result_fn
        self.loss_fn = loss_fn
        self.device=device
        self.logger = self._setup_logger(log_file)

    def _setup_logger(self, log_file):
        """
        Sets up a logger for both console and optional file logging.

        Parameters:
        -----------
        log_file : str or None
            If provided, logs are written to this file with rotation.

        Returns:
        --------
        logger : logging.Logger
        """
        logger = logging.getLogger("SimplaceOptimizer")
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # Optional file handler
        if log_file:
            fh = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        return logger

    def update_single_value_param(self, root, param_id, crop_name, new_value):
        """
        Updates a single-value parameter in the XML tree.

        Parameters:
        -----------
        root : lxml.etree.Element
            The root element of the parsed XML tree.
        param_id : str
            The ID of the parameter to update.
        crop_name : str
            The crop name to match.
        new_value : int or float
            The new value to assign to the parameter.
        """
        xpath = f"//crop[parameter[@id='CropName' and text()='{crop_name}']]/parameter[@id='{param_id}']"
        for param in root.xpath(xpath):
            if not param.getchildren():
                param.text = str(new_value)

    def update_multi_value_param(self, root, param_id, crop_name, new_values):
        """
        Updates a multi-value parameter in the XML tree.

        Parameters:
        -----------
        root : lxml.etree.Element
            The root element of the parsed XML tree.
        param_id : str
            The ID of the parameter to update.
        crop_name : str
            The crop name to match.
        new_values : list of int or float
            The new values to assign to the parameter.
        """
        xpath = f"//crop[parameter[@id='CropName' and text()='{crop_name}']]/parameter[@id='{param_id}']"
        for param in root.xpath(xpath):
            value_elements = param.findall('value')
            for i, val in enumerate(new_values):
                if i < len(value_elements):
                    value_elements[i].text = str(val)
                else:
                    new_elem = etree.SubElement(param, 'value')
                    new_elem.text = str(val)
            # Remove any extra old values
            for extra in value_elements[len(new_values):]:
                param.remove(extra)

    def run_simplace(self):
        """
        Executes the external simulation script (simplace_run.py).

        Raises:
        -------
        RuntimeError if the subprocess fails.
        """
        self.logger.info("Starting Simplace subprocess...")
        
        if self.device=='local':
            result = subprocess.run(
                ["python", "simplace_runner.py", self.config_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.logger.error("Simplace subprocess failed.")
                raise RuntimeError("Simplace run failed. Check stderr for details.")

            self.logger.info("Simplace subprocess completed successfully.")
        
        elif self.device=='cluster':
            result = subprocess.run(
                ["bash", "/path/start_example.sh"],
                capture_output=True,
                text=True
            )
            

    def objective(self, trial):
        """
        The Optuna objective function for a single optimization trial.

        Parameters:
        -----------
        trial : optuna.trial.Trial
            Optuna trial object to sample hyperparameters.

        Returns:
        --------
        float
            The computed loss for the current set of parameters.
        """
        # Load and parse XML
        tree = etree.parse(self.xml_path)
        root = tree.getroot()

        # Load optimization config
        with open(self.config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
        
        crop_name = config['crop_name']
        config = config[self.device]
        
        single_value_params = config.get('single_value_params', {})
        multi_value_params = config.get('multi_value_params', {})

        # Suggest and set single-value parameters
        for param_id, param_spec in single_value_params.items():
            if param_spec['type'] == 'int':
                suggested_value = trial.suggest_int(param_id, param_spec['low'], param_spec['high'])
            elif param_spec['type'] == 'float':
                precision = param_spec.get('precision', 4)
                suggested_value = round(trial.suggest_float(param_id, param_spec['low'], param_spec['high']), precision)

            self.update_single_value_param(root, param_id, crop_name, suggested_value)

        # Suggest and set multi-value parameters
        for param_id, param_spec in multi_value_params.items():
            suggested_values = []
            if param_spec['type'] == 'int':
                for i, bounds in enumerate(param_spec['values']):
                    val = trial.suggest_int(f"{param_id}_{i}", bounds['low'], bounds['high'])
                    suggested_values.append(val)
            elif param_spec['type'] == 'float':
                precision = param_spec.get('precision', 4)
                for i, bounds in enumerate(param_spec['values']):
                    val = round(trial.suggest_float(f"{param_id}_{i}", bounds['low'], bounds['high']), precision)
                    suggested_values.append(val)

            self.update_multi_value_param(root, param_id, crop_name, suggested_values)

        # Write the modified XML
        tree.write(self.xml_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')

        self.logger.info(f"Trial {trial.number}: Suggested parameters - {trial.params}")

        # Run the simulation
        self.run_simplace()
        
        best_trial = 0
        best_loss = 1e8
        
        # Process results and evaluate loss
        self.logger.info(f"Trial {trial.number}: Processing output...")
        result = self.process_result_fn()
        loss = self.loss_fn(result)

        if loss <= best_loss:
            best_loss = loss
            best_trial = trial.number
                    
        self.logger.info(f"Trial {trial.number} completed with loss: {loss:.4f}")
        self.logger.info(f"Best is trial {best_trial} with value: {best_loss:.4f}.\n")

        return loss

    def run_optimization(self, direction='minimize', n_trials=30, study_name=None, storage=None):
        """
        Runs the Optuna optimization loop.

        Parameters:
        -----------
        direction : str
            Direction of optimization ('minimize' or 'maximize').
        n_trials : int
            Number of trials to perform.
        study_name : str or None
            Optional name of the Optuna study.
        storage : str or None
            Optional database URL for persistent storage.

        Returns:
        --------
        optuna.study.Study
            The completed Optuna study object.
        """
        study = optuna.create_study(
            direction=direction,
            study_name=study_name,
            storage=storage
        )
        study.optimize(self.objective, n_trials=n_trials)
        
        return study
