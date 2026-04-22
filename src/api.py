import qbittorrentapi as qbitapi
import os
import logging

logger = logging.getLogger(__name__)
logger.info = print
logger.error = print
logger.debug = print

class APIWrapper:
    def __init__(self):
        self.username = os.environ.get("QBM_USERNAME")
        self.password = os.environ.get("QBM_PASSWORD")
        self.host = os.environ.get("QBM_HOST", "localhost")
        self.port = int(os.environ.get("QBM_PORT", "8080"))
        conn_info = dict(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
        )
        self.client = qbitapi.Client(**conn_info)
        self.try_login()
    
    def try_login(self):
        try:
            self.client.auth_log_in()
            logger.debug("Successfully Authenticated with qBittorrent instance")
        except qbittorrentapi.LoginFailed as e:
            logger.error("Failed to log into qBittorrent instance!")
            logger.error(str(e))
            raise e

    def display_conn_info(self):
        info = [f"qBittorrent: {self.client.app.version}", f"qBittorrent Web API: {self.client.app.web_api_version}"]

        for k, v in self.client.app.build_info.items():
            info.append(f"{k}: {v}")
        
        logger.info("\n".join(info))

if __name__ == "__main__":
    wrapper = APIWrapper()
    wrapper.display_conn_info()
