from huggingface_hub import hf_hub_download
import joblib
from config import get_hf_token

class ModelLoader:
    """
    A singleton class to load the yield prediction model and preprocessors
    from Hugging Face Hub. This ensures the models are loaded only once.
    """
    _instance = None

    def __init__(self):
        """Private constructor."""
        if ModelLoader._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.load_models()
            ModelLoader._instance = self

    def load_models(self):
        """Downloads and loads all necessary model files from Hugging Face."""
        try:
            token = get_hf_token()
        except ValueError:
            print("HUGGINGFACE_TOKEN not found in .env file. Proceeding without it for public repositories.")
            token = None
            
        repo_id = 'skcept/crop-yield-prediction'
        
        print("Downloading and loading models from Hugging Face Hub...")
        self.model = joblib.load(hf_hub_download(repo_id=repo_id, filename='knn.joblib', token=token))
        self.le_region = joblib.load(hf_hub_download(repo_id=repo_id, filename='le_Region.joblib', token=token))
        self.le_soil = joblib.load(hf_hub_download(repo_id=repo_id, filename='le_Soil_Type.joblib', token=token))
        self.le_crop = joblib.load(hf_hub_download(repo_id=repo_id, filename='le_Crop.joblib', token=token))
        self.le_weather = joblib.load(hf_hub_download(repo_id=repo_id, filename='le_Weather_Condition.joblib', token=token))
        self.scaler = joblib.load(hf_hub_download(repo_id=repo_id, filename='minmax_scaler.joblib', token=token))
        print("All yield prediction models and preprocessors loaded.")

    @classmethod
    def get_instance(cls):
        """Gets the single instance of the ModelLoader."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
