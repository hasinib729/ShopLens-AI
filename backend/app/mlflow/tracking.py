import os
import json
import time
import datetime
import platform
import subprocess
from typing import Dict, Any, Optional
from app.utils.config import settings

# Try loading MLflow
MLFLOW_AVAILABLE = False
try:
    import mlflow
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    MLFLOW_AVAILABLE = True
except ImportError:
    pass

class MLflowTracker:
    @staticmethod
    def get_git_commit() -> str:
        """Retrieves active Git commit hash if running in a repo."""
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
        except Exception:
            return "unknown-commit"

    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """Collects hardware info for experiment tracking metadata."""
        return {
            "os": platform.system(),
            "os_release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": str(os.cpu_count())
        }

    @classmethod
    def start_run(cls, experiment_name: str, run_name: Optional[str] = None):
        """Starts tracking run. Uses local JSON files if MLflow is unavailable."""
        if MLFLOW_AVAILABLE:
            try:
                mlflow.set_experiment(experiment_name)
                return mlflow.start_run(run_name=run_name)
            except Exception as e:
                print(f"MLflow start run error: {e}. Falling back to local file logger.")
                
        # Local JSON run mock
        return MockRun(experiment_name, run_name)

class MockRun:
    def __init__(self, experiment_name: str, run_name: Optional[str] = None):
        self.experiment_name = experiment_name
        self.run_name = run_name or f"run_{int(time.time())}"
        self.params = {}
        self.metrics = {}
        self.tags = {
            "git_commit": MLflowTracker.get_git_commit(),
            **MLflowTracker.get_system_info(),
            "start_time": datetime.datetime.utcnow().isoformat()
        }
        self.artifacts_dir = os.path.join(settings.LOCAL_STORAGE_DIR, "reports")
        os.makedirs(self.artifacts_dir, exist_ok=True)

    def log_param(self, key: str, value: Any):
        self.params[key] = str(value)
        print(f"[MockMLflow-Param] {key}: {value}")

    def log_metric(self, key: str, value: float, step: Optional[int] = None):
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append({"value": value, "step": step, "time": time.time()})
        print(f"[MockMLflow-Metric] {key}: {value}")

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        print(f"[MockMLflow-Artifact] Saved local file {local_path} under {artifact_path}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tags["end_time"] = datetime.datetime.utcnow().isoformat()
        self.save_run()

    def save_run(self):
        run_file = os.path.join(self.artifacts_dir, "mlflow_runs.json")
        runs = []
        
        if os.path.exists(run_file):
            try:
                with open(run_file, "r") as f:
                    runs = json.load(f)
            except Exception:
                pass
                
        run_data = {
            "experiment_name": self.experiment_name,
            "run_name": self.run_name,
            "params": self.params,
            "metrics": self.metrics,
            "tags": self.tags
        }
        runs.append(run_data)
        
        with open(run_file, "w") as f:
            json.dump(runs, f, indent=2)
        print(f"[MockMLflow] Logged run {self.run_name} to local runs file: {run_file}")
