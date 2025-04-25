from datetime import datetime, timedelta
import zxcvbn
import re
from app.auth import get_password_hash
from .database import db
from .logger import get_logger

class PasswordPolicy:
    """Class to manage password policies and validation."""
    
    # Define strength levels for password validation
    # These levels can be used to categorize the strength of a password
    STRENGTH_LEVELS = {
        0: "Very Weak",
        1: "Weak",
        2: "Medium",
        3: "Strong",
        4: "Very Strong"
    }
    
    def __init__(self, policy_id="default"):
        """Initialize with default or loaded configuration from MongoDB.
        
        Args:
            policy_id: The identifier for the policy configuration in the database
        """
        # Initialize logger
        self.logger = get_logger(__name__)
        
        # Ensure policy collection exists
        if 'password_policies' not in db.list_collection_names():
            self.logger.info("Creating password_policies collection")
            db.create_collection('password_policies')
        
        self.policy_collection = db['password_policies']
        self.policy_id = policy_id
        
        # Default configuration
        self.config = {
            "_id": policy_id,
            "min_length": 8,
            "min_score": 3,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digits": True,
            "require_special": True,
            "max_password_age_days": 90,
            "password_history_count": 5,
            "policy_version": "1.0"
        }
        
        # Load configuration from MongoDB if it exists
        stored_config = self.policy_collection.find_one({"_id": policy_id})
        if stored_config:
            self.logger.info(f"Loaded password policy configuration: {policy_id}")
            self.config = stored_config
        else:
            # Initialize with default settings
            self.logger.info(f"No configuration found for {policy_id}, using defaults")
            self.save_config()
    
    def save_config(self):
        """Save the current configuration to MongoDB."""
        try:
            # Update the configuration if it exists, otherwise insert it
            result = self.policy_collection.replace_one(
                {"_id": self.policy_id}, 
                self.config, 
                upsert=True
            )
            
            if result.modified_count:
                self.logger.info(f"Updated password policy: {self.policy_id}")
            elif result.upserted_id:
                self.logger.info(f"Created new password policy: {self.policy_id}")
            else:
                self.logger.info(f"No changes to password policy: {self.policy_id}")
                
            return True
        except Exception as e:
            self.logger.error(f"Error saving password policy configuration: {e}")
            return False
        
    def validate_password(self, password, user_inputs=None):
        """Validate a password against the current policy."""
        errors = []
        
        # Check length
        if len(password) < self.config["min_length"]:
            errors.append(f"Password must be at least {self.config['min_length']} characters long")
        
        # Check character requirements
        if self.config["require_uppercase"] and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.config["require_lowercase"] and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.config["require_digits"] and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if self.config["require_special"] and not re.search(r'[^A-Za-z0-9]', password):
            errors.append("Password must contain at least one special character")
        
        # Check zxcvbn score
        user_inputs = user_inputs or []
        result = zxcvbn.zxcvbn(password, user_inputs)
        if result['score'] < self.config["min_score"]:
            errors.append(f"Password is too weak. {result['feedback']['warning'] or ''}")
            if result['feedback']['suggestions']:
                errors.extend(result['feedback']['suggestions'])
        
        return (len(errors) == 0, errors)
    
    def calculate_strength(self, password, user_inputs=None):
        """Calculate the strength of a password using zxcvbn."""
        user_inputs = user_inputs or []
        result = zxcvbn.zxcvbn(password, user_inputs)
        
        return {
            'score': result['score'],
            'strength_level': self.STRENGTH_LEVELS[result['score']],
            'crack_time_display': result['crack_times_display']['offline_slow_hashing_1e4_per_second'],
            'feedback': result['feedback']
        }
    
    def check_password_reuse(self, new_password, password_history):
        """Check if a password exists in the user's password history.
        
        TODO: Implement password history"""
        new_hash = get_password_hash(new_password)
        return new_hash in password_history
    
    def needs_password_update(self, user_policy_version, password_date):
        """Check if a password needs to be updated based on policy changes or age."""
        # Check if policy has changed
        if user_policy_version != self.config["policy_version"]:
            return True, "Password policy has been updated"
        
        # Check password age
        if password_date and self.config["max_password_age_days"]:
            expiration_date = password_date + timedelta(days=self.config["max_password_age_days"])
            if datetime.now() > expiration_date:
                return True, f"Password has expired (maximum age is {self.config['max_password_age_days']} days)"
        
        return False, ""
    
    def update_policy(self, **kwargs):
        """Update policy settings."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        
        # When policy is updated, increment version
        # This is a simple versioning scheme; in practice, use semantic versioning
        major, minor = self.config["policy_version"].split(".")
        self.config["policy_version"] = f"{major}.{int(minor) + 1}"