import evaluate
from datasets import load_dataset, load_from_disk
import time
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, \
    DataCollatorForTokenClassification, AutoModelForTokenClassification, EvalPrediction, EarlyStoppingCallback
from configuration.config import *

# 分词器
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

# 标签映射
id2label = {id: label for id, label in enumerate(LABELS)}
label2id = {label: id for id, label in enumerate(LABELS)}

# 模型
model = AutoModelForTokenClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(LABELS),
    label2id=label2id,
    id2label=id2label,
)

# 3.加载数据集
train_dataset = load_from_disk(PROCESSED_DATA_DIR / "train")
val_dataset = load_from_disk(PROCESSED_DATA_DIR / "valid")

# 数据整理器
data_collator = DataCollatorForTokenClassification(
    tokenizer=tokenizer,
    padding=True,
    return_tensors="pt",
)


# 定义参数
args = TrainingArguments(
    output_dir=str(CHECKPOINT_LOG_DIR / NER_DIR),
    logging_dir=str(LOG_DIR / NER_DIR / time.strftime("%Y-%m-%d-%H-%M-%S")),
    per_device_train_batch_size=BATCH_SIZE,
    num_train_epochs=EPOCHS,

    save_strategy="steps",      # 保存策略
    save_steps=SAVE_STEPS,      # 每20个迭代进行一次保存
    save_total_limit=3,         # 最多保存3个检查点

    fp16=True,                  # 开启混合精度训练

    logging_strategy="steps",   # 日志写入策略
    logging_steps=SAVE_STEPS,   # 日志写入目录

    eval_strategy="steps",      # 评估策略
    eval_steps=SAVE_STEPS,      # 评估频率

    metric_for_best_model="eval_overall_f1", # 模型评估指标
    greater_is_better=True,     # 若是评估指标则True loss的话为False

    load_best_model_at_end=True,# 训练结束加载最佳模型

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
        unpad_label=[id2label[id] for id in unpad_label]
        unpad_pred=[id2label[id] for id in unpad_pred]
        # 添加到列表
        unpad_labels.append(unpad_label)
        unpad_preds.append(unpad_pred)
    result =seqeval.compute(predictions=unpad_preds, references=unpad_labels)
    return result
# 早停效果
early_stopping_callback = EarlyStoppingCallback(early_stopping_patience=2)

# 训练器
trainer = Trainer(
    model=model,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    args=args,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    callbacks=[early_stopping_callback],# 早停策略
)

trainer.train()

# 模型保存
trainer.save_model(CHECKPOINT_LOG_DIR / NER_DIR / "best.pt")
# if __name__ == '__main__':
#     pass
