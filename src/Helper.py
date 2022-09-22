import socket
import os
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from datetime import date, datetime, timedelta, timezone
from Configuration import Configuration
from export_queries import ALL_QUERIES
from Model import Query


class Helper:
    def __init__(self, configurations: Configuration, logger: Logger):
        self.logger = logger
        self.configuration = configurations

    def isWorkstation(self):
        """ For now, just check if a hostname starts with ABCD
        """
        hostname = socket.gethostname()
        if hostname.lower()[:4] in ("abcd"):
            return False if 'NO_WORKSTATION' in os.environ else True
        else:
            return False

    def get_azcredentials(self):
        """Obtain Azure Managed Identity Credentials 
        on ABN laptop somehow ManagedIdentityCredential does not work as it stucks between underlying api call
        and it never returns result, so checking isworkstation() to run it on local machine
        On Cluster it will get Pod Identity assigned to this pod
        """
        if self.isWorkstation():
            return DefaultAzureCredential(exclude_managed_identity_credential=True)
        else:
            return ManagedIdentityCredential(managed_identity_client_id=self.configuration.client_id)

    def get_keyvault_secret(self, vault_name: str, secret_name: str, credentials: ManagedIdentityCredential):
        """Obtain a secret from an Azure Key Vault

        Args:
            vault_name (str): Azure Key Vault Name
            secret_name (str): Azure Secret Name
            credentials (ManagedIdentityCredential): Azure Managed Identity Credentials
        """
        vault_url = f"https://{vault_name}.vault.azure.net"
        secret_client = SecretClient(
            vault_url=vault_url, credential=credentials, connection_verify=False
        )
        self.logger.info(f"Getting the secret for {secret_name}")
        secret_key = secret_client.get_secret(secret_name).value
        return secret_key

    def get_current_timezone_info(self):
        """
            Get Current TimeZone Information, CEST
        """
        timezone_offset = +2.0  # CEST
        tzinfo = timezone(timedelta(hours=timezone_offset))
        return tzinfo

    def build_directory_path(self, containername, query_version):
        """
            Build directory path where data needs to be exported
        """
        todays_date = date.today()
        year = todays_date.year
        month = todays_date.month
        day = todays_date.day

        date_time = datetime.now(self.get_current_timezone_info())
        hr = date_time.hour
        directory_structure = "{query_version}/WorkspaceResourceId=/subscriptions/{subscriptionid}/resourcegroups/{resourcegroup}/providers/microsoft.operationalinsights/workspaces/demo-la/y={year}/m={month}/d={day}/h={hr}".format(
            query_version=query_version, subscriptionid=self.configuration.subscription_id, resourcegroup=self.configuration.resource_group, dtap_letter=self.configuration.environment, blob_container_name=containername, year=year, month=month, day=day, hr=hr)
        return directory_structure

    def get_last_run_timestamp(self, blob_handler):
        """
            Get last run timestamp from state.ini file
        """
        ini_file = blob_handler.read_blob("state.ini")
        return ini_file

    def generate_state_file(self, blob_handler, start_export_time):
        """Generate State file to have checkpoint for the last run
        """
        statefile = f"state.ini"
        # Upload backfill statefile
        local_file_path = "state.ini"
        with open(local_file_path, "w") as state_file:
            state_file.write(
                f"Last Run;{start_export_time}")

        self.logger.info(f"Started uploading blob {statefile}")

        try:
            blob_handler.upload_blob(local_file_path, statefile)
            self.logger.info("successfully uploaded state file")
        except Exception as err:
            self.logger.error(err)

    def get_queries(self):
        """
            Get List of Queries which needs to be processed
        """
        queries = []
        for object in ALL_QUERIES:
            replaced_token_query = self.replace_tokens(object.get("Query"))
            query = Query(object.get("QueryName").strip(), object.get("QueryVersion").strip(), object.get(
                "QueryDurationInMins"), replaced_token_query, object.get("DestinationStorageLocation"))
            queries.append(query)
        return queries
    
    def replace_tokens(self, input):
        """
        Replace dtap_letter within query so same query can be used acroos differnt environments
        """
        return input.replace("#dtap_letter#", self.configuration.environment)
