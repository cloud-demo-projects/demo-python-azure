import os

class Configuration:
    LOCAL_FILE_NAME = "PT5M.json"
    FIRST_BACKFILL_DURATION = 90

    def __init__(self):
        self.environment = self.get_env_variable("dtap_letter")
        self.storage_account_name = self.get_env_variable("sa_name")
        self.keyvault_name = self.get_env_variable("kv_name")
        self.log_analytics_secret_name = self.get_env_variable("lw_name")
        self.client_id = self.get_env_variable("CLIENT_ID")
        self.subscription_id = self.get_env_variable("subscription_id")
        self.resource_group = self.get_env_variable("resource_group")
        self.first_backfill = self.get_env_variable("first_backfill")

    def get_env_specific_prop(self, property):
        """
        return property with environment specific letter within
        """
        return property.format(dtap_letter= self.environment)
    
    def get_env_variable(self, variable):
        """
        Get Environment Variable
        """
        return os.environ[variable]
