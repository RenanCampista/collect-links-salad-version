import requests
import logging


class ApiDbClient:
    """Client to interact with a REST API using a secret token for authentication."""
    def __init__(self, base_url: str, secret_token: str, logger: logging.Logger):
        self.base = base_url
        self.secret_token = secret_token
        self.headers = {
            'Authorization': f'Bearer {self.secret_token}',
            'Content-Type': 'application/json'
        }
        self.log = logger

    def send_posts(self, data: dict, route: str) -> bool:
        """Sends JSON data to the API, splitting into batches of 150 items if necessary."""
        try:
            response = requests.post(
                url=f"{self.base}/{route}", 
                json=data, 
                headers=self.headers, 
                timeout=30000
            )
            if response.status_code == 200:
                resp = response.json()
                resp = resp.get("resposta", "")
                if resp:
                    self.log.info("Resposta da API:")
                    for item, value in resp.items():
                        self.log.info(f"\t{item}: {value}")
                return True
            else:
                self.log.error(f"Erro ao enviar os dados: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.Timeout:
            self.log.error(f"Timeout ao enviar os dados. A API demorou mais de 5 minutos para responder.")
            return False
        except Exception as e:
            self.log.error(f"Erro ao enviar os dados: {e}")
            return False
        
    def get_posts(self, route: str) -> dict:
        """Fetches posts from the API."""
        try:
            response = requests.get(
                url=f"{self.base}/{route}", 
                headers=self.headers, 
                timeout=30000
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                resp = response.json()
                if resp.get('message', '') == 'Nenhum documento encontrado':
                    return {}
                else:
                    self.log.error(f"Erro ao buscar os dados: {response.status_code} - {response.text}")
                    return {}
            else:
                self.log.error(f"Erro ao buscar os dados: {response.status_code} - {response.text}")
                return {}
        except requests.exceptions.Timeout:
            self.log.error(f"Timeout ao buscar os dados. A API demorou mais de 5 minutos para responder.")
            return {}
        except Exception as e:
            self.log.error(f"Erro ao buscar os dados: {e}")
            return {}
        
    def delete_post(self, route: str, post_id: str) -> bool:
        """Deletes a post from the API."""
        try:
            params = {'post_id': post_id}
            response = requests.delete(
                url=f"{self.base}/{route}", 
                headers=self.headers, 
                params=params, 
                timeout=30000
            )
            if response.status_code == 200:
                return True
            else:
                self.log.error(f"Erro ao deletar o post: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.Timeout:
            self.log.error(f"Timeout ao deletar o post. A API demorou mais de 5 minutos para responder.")
            return False
        except Exception as e:
            self.log.error(f"Erro ao deletar o post: {e}")
            return False