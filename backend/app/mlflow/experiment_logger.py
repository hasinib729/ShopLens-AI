from typing import Dict, Any, Optional
from app.mlflow.tracking import MLflowTracker

class ExperimentLogger:
    @staticmethod
    def log_training_run(experiment_name: str, 
                         run_name: str, 
                         hyperparameters: Dict[str, Any], 
                         metrics: Dict[str, float], 
                         artifacts: Optional[Dict[str, str]] = None):
        """
        Logs a completed training execution run with parameters, metrics, and models.
        """
        with MLflowTracker.start_run(experiment_name, run_name) as run:
            # 1. Log hyperparameters
            for key, val in hyperparameters.items():
                run.log_param(key, val)
                
            # 2. Log final evaluation metrics
            for key, val in metrics.items():
                run.log_metric(key, val)
                
            # 3. Log artifacts
            if artifacts:
                for name, path in artifacts.items():
                    run.log_artifact(path, artifact_path=name)
                    
        print(f"Logged training run '{run_name}' to experiment '{experiment_name}' successfully.")
