import pandas as pd
import sys

def parse_original_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        sections = content.split('---------------')
        turns = [turn for turn in sections]  # 保留原始换行符
        return turns

def find_turn(turns, span_start):
    current_len = 0
    for i, turn in enumerate(turns):
        turn_len = len(turn) + turn.count('\n')  # 包括换行符的长度
        # 分隔符的长度，加上换行符的长度，如果不是第一个turn
        current_len += turn_len + (16 if i > 0 else 0)  # 分隔符'---------------' + 换行符
        if current_len >= span_start:
            return i
    return -1

def parse_annotation(file_path, turns):
    annotations = []
    belongto = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:



            line = line.replace('\t', ' ')

            parts = line.strip().split(' ')
            tag = parts[0]
            label = parts[1]

            if tag.startswith('E'):
                for item in parts[1:]:
                    _, sub_tag = item.split(':')
                    for ann in annotations:
                        if ann['ann_id'] == sub_tag:
                            ann['event'] = tag
                continue

            if tag.startswith('A'):
                tag2, value = parts[2], parts[3]
                for ann in annotations:
                    if ann['event'] == tag2:
                        ann['Val'] = value
                continue

            
            span_info = ' '.join(parts[2:]).split(';')
            contents = parts[-len(span_info):]
            for span, content in zip(span_info, contents):
                span_start, span_end = span.split()[:2]
                content = content.strip()
                span_start, span_end = int(span_start), int(span_end)
                turn_id = find_turn(turns, span_start)
                annotations.append({
                    'ann_id': tag,
                    'turn_id': turn_id,
                    'label': label,
                    'content': content,
                    'span_start': span_start,
                    'span_end': span_end,
                    'Val': '',
                    'event': ''
                })
    
    return annotations

def save_to_excel(annotations, file_path):
    df = pd.DataFrame(annotations)
    df = df.sort_values(by='span_start').reset_index(drop=True)
    df.to_excel(file_path, index=False)

def main():
    original_data_file = sys.argv[1]
    annotation_file = sys.argv[2]
    output_file = sys.argv[3]
    
    turns = parse_original_data(original_data_file)
    annotations = parse_annotation(annotation_file, turns)
    save_to_excel(annotations, output_file)

if __name__ == "__main__":
    main()
