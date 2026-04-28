from datasets import load_dataset
from transformers import AutoTokenizer
from configuration.config import  *


def process():
    dataset = load_dataset("json",data_files=RAW_DATA_FILE)

    # 去除多余的列
    dataset = dataset.remove_columns(['id', 'annotator', 'annotation_id', 'created_at', 'updated_at', 'lead_time'])
    # print(dataset)

    # 划分数据集
    dataset_dict = dataset["train"].train_test_split(test_size=0.2)
    dataset_dict["test"],dataset_dict["valid"] = dataset_dict["test"].train_test_split(test_size=0.5).values()

    # 分词器
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # 数据编码(输入和标签)
    def encode(example):
        # 将文本数据转成字符列表
        tokens = list(example["text"])
        # 文本编码
        inputs = tokenizer(tokens, is_split_into_words=True, truncation=True)
        # 进行实体标注
        entities = example["label"]
        # 定义标注列表
        labels = [LABELS.index("O")] *len(tokens)
        # 遍历每个TAG标记为"B"和“I”的ID
        for entity in entities:
            start =entity["start"]
            end =entity["end"]
            labels[start:end] = [LABELS.index("B")] + [LABELS.index("I")]*(end - start-1)
        # bert前后应该添加id-100对应CLS与SEP
        labels = [-100] + labels + [-100]
        inputs["labels"] = labels
        return  inputs
    dataset_dict = dataset_dict.map(encode,remove_columns=["text","label"])
    print(dataset_dict["train"][0])
    dataset_dict.save_to_disk(PROCESSED_DATA_DIR)


if __name__ == '__main__':
    process()