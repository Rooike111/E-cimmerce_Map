import torch
from transformers import AutoTokenizer,AutoModelForTokenClassification
from configuration.config import *
from utils import MysqlReader,Neo4jWriter
from ner.predict import Predictor

class TextSynchronizer:
    def __init__(self):
        self.reader = MysqlReader()
        self.writer = Neo4jWriter()
        # 定义一个实体的提取器
        self.extractor = self._init_extractor()

    def _init_extractor(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = AutoModelForTokenClassification.from_pretrained(str(CHECKPOINT_LOG_DIR/NER_DIR/ "best.pt"))
        tokenizer = AutoTokenizer.from_pretrained(str(CHECKPOINT_LOG_DIR/NER_DIR/ "best.pt"))
        return Predictor(model=model, tokenizer=tokenizer, device=device)

    # 同步Tag 标签
    def sync_tag(self):
        # 1. 从MySQL提取商品信息
        sql = """
            select id,description
            from spu_info
        """
        spu_desc = self.reader.read(sql)
        # 2. 拆分spu_id 和desc
        ids = [item["id"] for item in spu_desc]
        desc = [item["description"] for item in spu_desc]

        # 3.提取所有数据的Tag列表
        tags_list = self.extractor.extract(desc)
        # for id,tag in zip(ids, tags_list):
        #     print(id,tag)

        # 4. 构建Tag节点属性(id,name)以及SPU->Tag
        tag_properties=[]
        relations = []
        for id, tags in zip(ids, tags_list):
            for index,tag in enumerate(tags):
                tag_id = "-".join([str(id), str(index)])
                property = {"id": tag_id, "name": tag}
                tag_properties.append(property)
                # 构建关系
                relation = {"start_id": id, "end_id": tag_id}
                relations.append(relation)
        # 写入Neo4j
        self.writer.write_node("Tag",tag_properties)
        self.writer.write_relation("Have","SPU","Tag",relations)

if __name__ == '__main__':
    synchronizer = TextSynchronizer()
    synchronizer.sync_tag()