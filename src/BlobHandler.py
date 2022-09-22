from azure.storage.blob import BlobServiceClient


class BlobHandler:
    """A handler that helps interacting with a Azure Blob Storage account

    Args:
        storage_account (str): Name of the Azure Blob Storage account
        container (str): Name of the container
        credentials (ManagedIdentityCredential): Azure Managed Identity Credentials
    """

    def __init__(self, storage_account, container, credentials, logger: Logger):

        self.container = container
        self.logger = logger

        self.service_client = BlobServiceClient(
            account_url=(f"https://{storage_account}.blob.core.windows.net/"),
            credential=credentials,
        )
        self.container_client = self.service_client.get_container_client(
            container=container
        )

    def upload_blob(self, input_file_path, blob_path, overwrite=True):
        """Upload a file as blob to the Blob Storage account

        Args:
            input_file_path (str): Provide the path of the local file
            blob_path (str): Provide the full folder path in the container.
                exp: export/table_name/file.json
        """
        blob_client = self.service_client.get_blob_client(
            container=self.container, blob=f"{blob_path}"
        )

        with open(input_file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=overwrite)

        if blob_client.exists():
            self.logger.info(f"Blob uploaded successfully:{blob_path}")
        else:
            self.logger.error(f"Could not upload Blob:{blob_path}")

    def delete_blob(self, blob_path):
        """Delete a blob in the Blob Storage account

        Args:
            blob_path (str): Provide the full folder path in the container.
                exp: export/table_name/file.json
        """
        blob_client = self.service_client.get_blob_client(
            container=self.container, blob=f"{blob_path}"
        )

        blob_client.delete_blob()

        if not blob_client.exists():
            self.logger.info(f"Blob deleted successfully: {blob_path}")
        else:
            self.logger.error(f"Could not delete blob: {blob_path}")

    def list_blobs(self):
        """Returns a list of all blob file paths inside the container"""
        blobs = [blob.name for blob in self.container_client.list_blobs()]
        return blobs

    def read_blob(self, file_to_read):
        """
            Returns stream of data from the blob container
        """
        blob_client = self.service_client.get_blob_client(
            container=self.container, blob=f"{file_to_read}"
        )

        blob_content = None
        with open(file_to_read, "wb") as f:
            try:
                blob_download = blob_client.download_blob()
                blob_content = blob_download.readall().decode("utf-8")
                self.logger.info(f"state ini content is: '{blob_content}'")
            except Exception as err:
                self.logger.info(err)

        return blob_content
