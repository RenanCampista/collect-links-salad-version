import time
import logging
from dotenv import load_dotenv
import os

from src.api_db_client import ApiDbClient
from src.utils import setup_logging, format_posts, handle_rate_limit_restart
from src.instagram_link_fetcher import InstagramLinkFetcher


log = logging.getLogger(__name__)
log = setup_logging("logs/bio_collector_instaloader", "bio_collector")

def load_env_variables() -> dict:
    load_dotenv()
    config = {
        "API_BASE_URL": os.getenv("API_BASE_URL"),
        "SECRET_TOKEN": os.getenv("SECRET_TOKEN"),
    }
    return config


def delete_processed_posts(api_client: ApiDbClient, posts: list[dict], log: logging.Logger):
    """Deleta posts do banco provisório após coletar os links."""
    for post in posts:
        if api_client.delete_post("instagram/coleta_links/delete", post['postId']):
            log.info(f"✓ Post deletado (postId: {post.get('postId', 'N/A')})")
        else:
            log.error(f"✗ Erro ao deletar post (postId: {post.get('postId', 'N/A')})")


def main():
    configs = load_env_variables()
    api_client = ApiDbClient(configs["API_BASE_URL"], configs["SECRET_TOKEN"], log)
    ig_fetcher = InstagramLinkFetcher(log)
    counter = 0
    
    while True:
        response = api_client.get_posts("instagram/coleta_links/get")

        if not response:
            log.info("Nenhum post para processar. Aguardando 2 minutos...")
            counter += 1
            if counter >= 2:
                log.info("Nenhum post processado por 4 minutos. Reiniciando processo para evitar possíveis bloqueios.")
                handle_rate_limit_restart()
            time.sleep(20)
            continue
        
        log.info(f"Processando {response.get('total', 0)} posts de @{response.get('username', '')}")
        
        updated_posts, rate_limit = ig_fetcher.search_links(
            posts_data=response.get('result', []),
            username=response.get('username', ''), 
            max_retries=3   
        )
        
        if rate_limit:
            handle_rate_limit_restart()
        
        formatted_posts = format_posts(updated_posts)
        
        if api_client.send_posts(formatted_posts, "instagram/post/json"):
            delete_processed_posts(api_client, updated_posts, log)
            log.info("Posts atualizados enviados com sucesso para a API.")
        else:
            log.error("Erro ao enviar posts atualizados para a API.")
            
            
if __name__ == "__main__":
    main()