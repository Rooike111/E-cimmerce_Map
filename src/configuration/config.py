from pathlib import Path

# 1.目录路径
ROOT_DIR = Path(__file__).parent.parent.parent

DATA_DIR = ROOT_DIR / "data"
NER_DIR = "ner"
RAW_DATA_DIR = DATA_DIR / NER_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / NER_DIR / "processed"

LOG_DIR = ROOT_DIR / "logs"
CHECKPOINT_LOG_DIR = LOG_DIR / "checkpoints"

# 2.数据文件夹和模型名称
RAW_DATA_FILE = str(RAW_DATA_DIR / "data.json")
MODEL_NAME = "google-bert/bert-base-chinese"

# 3.超参数
BATCH_SIZE = 2
EPOCHS = 5
LR = 5e-5

SAVE_STEPS = 20

# NER任务分类标签
LABELS = ["B", "I", "O"]

# 数据库连接
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "passwd": "admin",
    "database": "gmall",
    "port": 3306
}

NEO4j_CONFIG = {
    'uri': "neo4j://localhost",
    'auth': ("neo4j", "wg1422874846")
}

DEEPSEEK_API_KEY = "sk-******"
DEEPSEEK_API_URL = "https://api.deepseek.com"

WEB_STATIC_DIR = ROOT_DIR / "src" / "web" / "static"
