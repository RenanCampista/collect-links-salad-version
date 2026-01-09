import logging
import os
from datetime import datetime
import unicodedata
import re
import sys


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
        
        # Extrair timestamp (pode vir como dict do MongoDB com "$date")
        timestamp = body_data.get('timestamp', '')
        if isinstance(timestamp, dict) and '$date' in timestamp:
            timestamp = timestamp['$date']
        
        # Extrair media (converter lista de dicts para string se necessário)
        media = body_data.get('media', '')
        if isinstance(media, list) and len(media) > 0:
            # Manter como lista se a API aceitar, ou converter para string separada por vírgula
            media = media  # A API espera lista ou string
        
        formatted_post = {
            "body": {
                "postShortcode": post.get('postShortcode', '').replace('@', ''),
                "name": body_data.get('authorName', ''),
                "time": timestamp,
                "likes": int(metadata.get('stats', {}).get('like', 0)),
                "message": body_data.get('text', ''),
                "profileId": body_data.get('authorId', ''),
                "commentId": "",
                "username": body_data.get('authorNickName', ''),
                "parentCommentId": "",
                "replies": "",
                "reply": "",
                "shortcode": post.get('postShortcode', ''),
                "reaction": "",
                "isVideo": body_data.get('isVideo', ''),
                "comments": int(metadata.get('stats', {}).get('comment', 0)),
                "url": body_data.get('postUrl', ''),
                "profileUrl": body_data.get('authorUrl', ''),
                "videoViewCount": int(metadata.get('stats', {}).get('seen', 0)),
                "isPrivateUser": "",
                "isVerifiedUser": "",
                "displayUrl": "",
                "followersCount": "",
                "id": int(post.get('postId', 0)) if post.get('postId', '').isdigit() else 0,
                "caption": "",
                "thumbnail": "",
                "accessibilityCaption": "",
                "commentsDisabled": "",
                "videoDuration": "",
                "isSponsored": body_data.get('isSponsored', ''),
                "locationName": body_data.get('locationName', ''),
                "mediaCount": "",
                "media": media,
                "owner": "",
                "profileImage": body_data.get('authorImage', ''),
                "terms": ""
            },
            "metadata": {
                "theme": "",
                "terms": [],
                "project": "uncategorized",
                "api_version": "painel-ContentLibrary"
            }
        }
        formatted_posts.append(formatted_post)
    
    return formatted_posts


def handle_rate_limit_restart():
    """Reinicia o container quando atinge rate limits."""
    sys.exit(2) # restart container