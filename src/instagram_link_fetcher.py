import io
import logging
import contextlib
import time
from difflib import SequenceMatcher
from itertools import islice
from .utils import clean_text, post_short_code

import instaloader
from instaloader import Instaloader


class InstagramLinkFetcher:
    """"Classe para coletar dados de perfis do Instagram usando Instaloader."""
    def __init__(self, logger: logging.Logger):
        self.loader = Instaloader()
        self.loader.context.sleep = True
        self.log = logger
    
    def check_rate_limit_in_output(self, error_message: str, captured_output: str = "") -> bool:
        """Verifica se o erro ou saída capturada contém indicadores de rate limit."""
        rate_limit_indicators = [
            "Please wait a few minutes before you try again",
            "429",
            "Too many requests",
            "401 Unauthorized"
        ]
        
        full_text = str(error_message).lower() + " " + captured_output.lower()
        return any(indicator.lower() in full_text for indicator in rate_limit_indicators)

    def search_links(
            self, 
            posts_data: list[dict], 
            username: str, 
            max_retries: int = 3, 
            timeout_seconds: int = 30
        ) -> tuple[list[dict], bool]:
        """Busca links nos posts do perfil; interrompe a busca após `timeout_seconds` e processa resultados parciais."""
        
        retries = 0
        while retries < max_retries:
            self.log.info(f"Buscando links para @{username} (tentativa {retries + 1}/{max_retries})...")
            try:
                # Redireciona stderr temporariamente para suprimir mensagens do Instaloader
                #with contextlib.redirect_stderr(io.StringIO()):
                profile = instaloader.Profile.from_username(self.loader.context, username)
                    
                # Para cada post que queremos encontrar, armazenar melhor match
                best_matches = {}
                for idx, post_data in enumerate(posts_data):
                    best_matches[idx] = {'url': None, 'score': 0.0}
                    
                # Itera pelos posts do perfil; interrompe se o timeout for atingido.
                start_time = time.time()
                #with contextlib.redirect_stderr(io.StringIO()):
                for post in islice(profile.get_posts(), 30):
                    # Verifica timeout
                    if time.time() - start_time > timeout_seconds:
                        self.log.warning(f"Timeout de {timeout_seconds}s atingido ao buscar posts; processando resultados parciais.")
                        break

                    if post.caption:
                        post_caption_clean = clean_text(post.caption)[:200]
                        post_url = f'https://www.instagram.com/p/{post.shortcode}/'

                        # Comparar com todos os posts que estamos procurando
                        for idx, post_data in enumerate(posts_data):
                            post_text = post_data['postHistory'][0]['body']['text'] if post_data['postHistory'] else ''
                            post_text_clean = clean_text(post_text)[:200]
                            score = SequenceMatcher(None, post_caption_clean, post_text_clean).ratio()

                            # Se encontrou um match melhor, atualizar
                            if score > best_matches[idx]['score']:
                                best_matches[idx]['score'] = score
                                best_matches[idx]['url'] = post_url
                                    
                # Processar resultados
                found_count = 0
                for idx, match_info in best_matches.items():
                    if match_info['score'] >= 0.50:
                        #posts_data[idx]['postUrl'] = match_info['url'] Não está acessando corretamente
                        posts_data[idx]['postHistory'][0]['body']['postUrl'] = match_info['url']
                        posts_data[idx]['postShortcode'] = post_short_code(match_info['url'])
                        found_count += 1
                        self.log.info(f"  ✓ Post encontrado (linha {idx + 1})")
                        
                        self.log.debug(f"melhor score: {match_info['score']:.2f}) -> {match_info['url']}")
                    else:
                        self.log.info(f"  ✗ Post não encontrado (linha {idx + 1})")
                        
                        self.log.debug(f"melhor score: {match_info['score']:.2f}) -> nenhum link")    
                             
                self.log.info(f"Resultado: {found_count}/{len(posts_data)} posts encontrados\n")
                
                return posts_data, False
            except Exception as e:
                captured_output = ""
                if self.check_rate_limit_in_output(e, captured_output):
                    self.log.warning(f"Rate limit atingido ao acessar o perfil '{username}'. Tentando novamente após espera.")
                    retries += 1
                    continue
                else:
                    self.log.error(f"Erro ao acessar o perfil '{username}': {e}")
                    return [], True
                
        return [], True