import logging
import os
from datetime import datetime
import unicodedata
import re

def setup_logging(log_dir: str, log_name: str) -> logging.Logger:
    """Configures logging with daily log files."""
    # Criar diretório se não existir
    os.makedirs(log_dir, exist_ok=True)
    
    # Gerar nome do arquivo com data atual
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{log_name}_{current_date}.log")
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding='utf-8')
        ],
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Log iniciado: {log_file}")
    return logger


def clean_text(text):
    """Limpa o texto removendo acentos e caracteres especiais."""
    text = str(text)
    # Remove acentos e caracteres especiais
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    # Remove outros símbolos
    text = re.sub(r'[^\w\s]', '', text)
    return text


def post_short_code(post_url: str) -> str:
    """Extrai o shortcode do post a partir da URL."""
    return post_url.rstrip('/').split('/')[-1]


def format_posts(posts: list[dict]) -> list[dict]:
    """Formata posts para o formato esperado pela API do Instagram Content Library."""
    formatted_posts = []
    for post in posts:
        if not post.get('postHistory') or len(post['postHistory']) == 0:
            continue
            
        body_data = post['postHistory'][0].get('body', {})
        metadata = post['postHistory'][0].get('metadata', {})
        
        formatted_post = {
            "body": {
                "postShortcode": post.get('postShortcode', ''),
                "name": body_data.get('authorName', ''),
                "time": body_data.get('timestamp', ''),
                "likes": metadata.get('stats', {}).get('like', 0),
                "message": body_data.get('text', ''),
                "profileId": body_data.get('authorId', ''),
                "commentId": "",
                "username": body_data.get('authorNickName', ''),
                "parentCommentId": "",
                "replies": "",
                "reply": body_data.get('reply', False),
                "shortcode": post.get('postShortcode', ''),
                "reaction": "",
                "isVideo": body_data.get('isVideo', False),
                "comments": metadata.get('stats', {}).get('comment', 0),
                "url": body_data.get('postUrl', ''),
                "profileUrl": body_data.get('authorUrl', ''),
                "videoViewCount": metadata.get('stats', {}).get('seen', 0),
                "isPrivateUser": "",
                "isVerifiedUser": "",
                "displayUrl": "",
                "followersCount": "",
                "id": post.get('postId', ''),
                "caption": "",
                "thumbnail": "",
                "accessibilityCaption": "",
                "commentsDisabled": "",
                "videoDuration": "",
                "isSponsored": body_data.get('isSponsored', False),
                "locationName": body_data.get('locationName', ''),
                "mediaCount": "",
                "media": body_data.get('media', []),
                "owner": "",
                "profileImage": body_data.get('authorImage', ''),
                "terms": post.get('terms', [])
            },
            "metadata": {
                "theme": metadata.get('collect', {}).get('theme'),
                "terms": post.get('terms', []),
                "project": "uncategorized",
                "api_version": metadata.get('collect', {}).get('apiVersion', 'painel-ContentLibrary')
            }
        }
        formatted_posts.append(formatted_post)
    
    return formatted_posts

