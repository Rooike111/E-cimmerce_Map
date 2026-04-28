import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from configuration.config import *
# 自定义预测器
class Predictor:
    def __init__(self,model,tokenizer,device):
        self.model=model.to(device).eval()
        self.tokenizer=tokenizer
        self.device=device
    #预测方法
    def predict(self,inputs:str|list[str]):
        is_str = isinstance(inputs,str)
        if is_str:
            inputs = [inputs]
        # 对其进行预分词
        tokens_list = [list(input) for input in inputs]
        inputs_token = self.tokenizer(
            tokens_list,
            is_split_into_words=True,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )
        inpout_tensor = {k:v.to(self.device) for k,v in inputs_token.items()}
        with torch.no_grad():
            model_output = self.model(**inputs_token)
            logits = model_output.logits
            preds = logits.argmax(dim=-1).tolist()

        # 将id列表转换为BIO标签
        final_predictions = []
        for tokens,pre in zip(tokens_list,preds):
            # 获取真实长度
            prediction = pre[1:len(tokens)+1]
            # 转换为标签
            final_prediction = [self.model.config.id2label[id] for id in prediction]
            final_predictions.append(final_prediction)

        if is_str:
            return final_predictions[0]
        return final_predictions

    def extract(self,inputs:str|list[str]):
        is_str = isinstance(inputs,str)
        if is_str:
            inputs = [inputs]
        predictions = self.predict(inputs)

        entities_list = []
        for prediction,input in zip(predictions,inputs):
            # 调用内部函数抽取一个样本的所有实体标签
            entities = self._extract_entities(list(input),prediction)
            entities_list.append(entities)
        if is_str:
            return entities_list[0]
        return entities_list

    def _extract_entities(self,tokens,prediction):
        entities = []
        current_entity=""
        for entity,label in zip(tokens,prediction):
            if label == "B":
                if current_entity :
                    entities.append(current_entity)
                current_entity = entity
            elif label == "I":
                if current_entity :
                    current_entity += entity
            else:
                if current_entity :
                    entities.append(current_entity)
                current_entity = ""
        if current_entity :
            entities.append(current_entity)
        return entities


def predict():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForTokenClassification.from_pretrained(str(CHECKPOINT_LOG_DIR/NER_DIR/"best.pt"))
    tokenizer = AutoTokenizer.from_pretrained(str(CHECKPOINT_LOG_DIR/NER_DIR/"best.pt"))

    predictor = Predictor(model,tokenizer,device)

    text = "麦德龙德国进口双心多维叶黄素护眼营养软胶囊30粒x3盒眼干涩"

    entities = predictor.extract(text)
    print(entities)

if __name__ == '__main__':
    predict()