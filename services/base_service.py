from db import save_model, load_model, delete_model

class BaseService:
    def __init__(self):
        pass  

    def save_model(self, user_token, run_id, model_data):
        """Handles storing the model in the database."""
        save_model(user_token, run_id, model_data)

    def load_model(self, user_token, run_id):
        """Retrieves the model from the database, returns None if not found."""
        return load_model(user_token, run_id)

    def delete_model(self, user_token, run_id):
        """Deletes model data from the database."""
        return delete_model(user_token, run_id)

    def authenticate_user(self, user_token, run_id):
        """Checks if the user has access to the model."""
        model = self.load_model(user_token, run_id)
        if model is None:
            return None  
        return model