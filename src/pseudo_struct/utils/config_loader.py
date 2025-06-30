# src/pseudo_struct/utils/config_loader.py

import os
import yaml
from pathlib import Path
from logger import get_logger

logger = get_logger("config_loader")

def deep_merge_dicts(base, override):
    """
    dict deep merge: base를 복사해 override와 재귀적으로 합침
    """
    merged = base.copy()
    for k, v in override.items():
        if (
            k in merged
            and isinstance(merged[k], dict)
            and isinstance(v, dict)
        ):
            merged[k] = deep_merge_dicts(merged[k], v)
        else:
            merged[k] = v
    return merged

def load_config(config_file="config/config.yml", env_var="PS_ENV", default_env="default"):
    """
    config.yml에서 환경별 값까지 deep merge하여 dict로 반환
    - config_file: yaml 파일 경로
    - env_var: 환경명을 지정하는 환경변수명(기본 PS_ENV)
    - default_env: fallback 환경명(기본 default)
    """
    ROOT = Path(__file__).resolve().parents[3]
    config_path = ROOT / config_file
    logger.debug(f"Config 파일 경로: {config_path}")

    # config.yml 존재 여부 체크
    if not config_path.exists():
        logger.error(f"Config 파일이 존재하지 않습니다: {config_path}")
        raise FileNotFoundError(f"Config 파일이 없습니다: {config_path}")

    # config.yml 파싱
    try:
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except Exception as e:
        logger.exception(f"Config 파일 파싱 오류: {e}")
        raise

    env = os.getenv(env_var, default_env)
    logger.info(f"설정 환경: {env}")

    if env not in cfg:
        logger.warning(f"지정된 환경({env})이 config.yml에 없으므로 default 환경({default_env})을 사용합니다.")
        env = default_env

    # deep merge
    base = cfg.get(default_env, {})
    over = cfg.get(env, {})
    merged = deep_merge_dicts(base, over)
    logger.debug(f"병합된 config: {merged}")

    return merged

# 사용 예시/디버깅
if __name__ == "__main__":
    try:
        config = load_config()
        logger.info(f"최종 config: {config}")
    except Exception as e:
        logger.critical(f"Config 로딩 실패: {e}")

