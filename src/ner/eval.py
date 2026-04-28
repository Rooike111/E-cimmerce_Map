import time

import evaluate
from datasets import load_from_disk
from transformers import Trainer, AutoTokenizer, AutoModelForTokenClassification, DataCollatorForTokenClassification, \
    TrainingArguments, EarlyStoppingCallback, EvalPrediction
from configuration.config import *
# 直接通过Trainer进行评估
# 验证评估



tokenizer = AutoTokenizer.from_pretrained(
    CHECKPOINT_LOG_DIR / NER_DIR / "best.pt"
)


# 模型
model = AutoModelForTokenClassification.from_pretrained(
    CHECKPOINT_LOG_DIR / NER_DIR / "best.pt"
)

# 3.加载数据集
test_dataset = load_from_disk(PROCESSED_DATA_DIR / "test")

# 数据整理器
data_collator = DataCollatorForTokenClassification(
    tokenizer=tokenizer,
    padding=True,
    return_tensors="pt",
)


# 评估指标
seqeval = evaluate.load("seqeval")

def compute_metrics(prediction:EvalPrediction):
    # 提取模型的预测输出与真实标签
    logits = prediction.predictions
    preds = logits.argmax(axis=-1)
    labels = prediction.label_ids
    # 将标签id转换为真正的标注标签 B I O
    unpad_labels = []
    unpad_preds = []
    for pred,label in zip(preds, labels):
        unpad_label = label[label != -100]
        unpad_pred = pred[label != -100]
        # 转BIO标签
        unpad_label=[model.config.id2label[id] for id in unpad_label]
        unpad_pred=[model.config.id2label[id] for id in unpad_pred]
        # 添加到列表
        unpad_labels.append(unpad_label)
        unpad_preds.append(unpad_pred)
    result =seqeval.compute(predictions=unpad_preds, references=unpad_labels)
    return result

# 训练器
trainer = Trainer(
    model=model,
    eval_dataset=test_dataset,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

result = trainer.evaluate()

print(result)