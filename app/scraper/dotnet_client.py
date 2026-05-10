import httpx
import structlog
from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

class DotNetClient:
    def __init__(self):
        self.base_url = settings.dotnet_backend_url.rstrip("/")
        self.email = settings.dotnet_login_email
        self.password = settings.dotnet_login_password
        self.token = None

    async def _authenticate(self, client: httpx.AsyncClient):
        logger.info("authenticating_with_dotnet", email=self.email, base_url=self.base_url)
        response = await client.post(
            f"{self.base_url}/api/auth/login",
            json={"email": self.email, "password": self.password}
        )
        response.raise_for_status()
        data = response.json()
        
        # Check standard .NET Core wrappers (success, data)
        if "data" in data and isinstance(data["data"], dict):
            inner_data = data["data"]
            self.token = inner_data.get("token") or inner_data.get("accessToken")
        else:
            self.token = data.get("token") or data.get("accessToken")
             
        if not self.token:
            logger.error("dotnet_auth_failed_no_token", response=data)
            raise ValueError("Could not extract token from login response")
            
        logger.info("dotnet_auth_successful")

    async def push_report(self, report_data: dict, image_files: list = None):
        """
        Push a scraped report to the .NET backend.
        report_data is sent as multipart/form-data as required by /api/Reports.
        image_files should be a list of tuples: (filename, file_bytes, content_type)
        """
        async with httpx.AsyncClient() as client:
            if not self.token:
                await self._authenticate(client)
            
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Use a list of tuples to support multiple files with the same key ("Images")
            multipart_data = []
            for k, v in report_data.items():
                if v is not None:
                    multipart_data.append((k, (None, str(v))))
                    
            if image_files:
                for img in image_files:
                    multipart_data.append(("Images", img))
            
            logger.info("pushing_report_to_dotnet", type=report_data.get("Type"), url=report_data.get("SourceUrl"), images_count=len(image_files) if image_files else 0)
            
            response = await client.post(
                f"{self.base_url}/api/Reports",
                files=multipart_data,
                headers=headers
            )
            
            if response.status_code == 401:
                # Token expired or invalid, retry once
                logger.warning("dotnet_token_expired_retrying")
                await self._authenticate(client)
                headers["Authorization"] = f"Bearer {self.token}"
                response = await client.post(
                    f"{self.base_url}/api/Reports",
                    files=multipart_data,
                    headers=headers
                )
                
            response.raise_for_status()
            response_json = response.json()
            logger.info("report_pushed_successfully", status_code=response.status_code, response=response_json)
            return response_json
