import os
import json
from typing import Optional
from app.utils.config import settings

# Global MLflow imports
MLFLOW_AVAILABLE = False
try:
    import mlflow
    from mlflow.tracking import MlflowClient
    MLFLOW_AVAILABLE = True
except ImportError:
    pass

class ModelRegistryManager:
    def __init__(self):
        self.registry_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "model_registry", 
            "active_models.json"
        )

    def register_model(self, model_name: str, model_local_path: str, run_id: Optional[str] = None):
        """Registers a trained model version."""
        if MLFLOW_AVAILABLE and run_id:
            try:
                # Log to MLflow Model Registry
                model_uri = f"runs:/{run_id}/{model_name}"
                mlflow.register_model(model_uri, model_name)
                print(f"Registered model {model_name} in MLflow Model Registry.")
            except Exception as e:
                print(f"MLflow model registration error: {e}. Registering locally.")
                
        # Always register locally for runtime loading
        self.register_locally(model_name, os.path.basename(model_local_path))

    def register_locally(self, model_type: str, version_filename: str):
        """Updates the local active_models.json registry file."""
        data = {}
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r") as f:
                    data = json.load(f)
            except Exception:
                pass
                
        # Map model type to registry keys
        key = None
        if "sentence" in model_type or "search" in model_type:
            key = "search_model"
        elif "clip" in model_type:
            key = "clip_model"
        elif "rank" in model_type:
            key = "ranker"
        elif "recommender" in model_type or "two_tower" in model_type:
            key = "recommender"
            
        if key:
            data[key] = version_filename
            
        # Ensure parent folder exists
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[LocalRegistry] Updated active model mapping locally: {key} -> {version_filename}")

    def transition_model_stage(self, model_name: str, version: int, stage: str):
        """Transitions model stage (Staging, Production) in MLflow."""
        if MLFLOW_AVAILABLE:
            try:
                client = MlflowClient()
                client.transition_model_version_stage(
                    name=model_name,
                    version=version,
                    stage=stage,
                    archive_existing_versions=True
                )
                print(f"Transitioned {model_name} version {version} to {stage}.")
            except Exception as e:
                print(f"MLflow transition stage error: {e}")
                
model_registry_manager = ModelRegistryManager()
