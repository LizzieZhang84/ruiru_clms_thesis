import pandas as pd
import sys
import os
import glob

def process_excel(file_path, output_folder):
    # 读取 Excel 文件
    df = pd.read_excel(file_path)

    # 提取数据
    def extract_content(label):
        filtered_df = df[df['label'] == label]
        if filtered_df.empty:
            return "无"
        return ','.join(filtered_df.sort_values('span_start')['content'].tolist())

    # 第一部分内容拼接
    patient_info = f"【病人信息】：{extract_content('Sex')},{extract_content('Age')}"
    medical_history = f"【病史】：{extract_content('Clinical_History')}"
    prior_diagnosis = f"【前期诊断】：{extract_content('Previous_Diagnosis')}"
    prior_treatment = f"【前期治疗】：{extract_content('Previous_Treatment')}"
    main_problem = f"【发帖人主要诉求】：{extract_content('Problem_Current')}"

    # 第二部分内容处理
    def get_val_text(val):
        val_map = {
            "possible": "可能是",
            "present": "是",
            "hypothetical_present": "是",
            "negated": "不是",
            "hypothetical_negated": "不是",
            "conditional": ""
        }
        return val_map.get(val, "未知")

    # 评论区诊断
    diagnosis_df = df[df['label'] == 'Diagnosis']
    
    # 统计每种诊断的数量
    diagnosis_counts = diagnosis_df.groupby(['content', 'Val']).size().reset_index(name='Count')
    diagnosis_counts['Val'] = diagnosis_counts['Val'].map(get_val_text)
    diagnosis_counts = diagnosis_counts.sort_values(by='Count', ascending=False)
    
    diagnosis_output = '\n'.join([f"{row['Count']}人认为{row['Val']}{row['content']}" for _, row in diagnosis_counts.iterrows()]) or "无"

    # 治疗方案
    treatment_df = df[df['label'] == 'Treatment']
    treatment_output = []
    for _, treatment_row in treatment_df.iterrows():
        event = treatment_row['event']
        if pd.notna(event):
            diagnosis_content = df[(df['label'] == 'Diagnosis') & (df['event'] == event)]['content']
            treatment_output.append(f"{treatment_row['content']}（{'，'.join(diagnosis_content) if not diagnosis_content.empty else '无'}）")
        else:
            treatment_output.append(treatment_row['content'])
    treatment_output = '\n'.join(treatment_output) or "无"

    # 检查建议
    test_df = df[df['label'] == 'Test']
    test_output = []
    for _, test_row in test_df.iterrows():
        event = test_row['event']
        if pd.notna(event):
            diagnosis_content = df[(df['label'] == 'Diagnosis') & (df['event'] == event)]['content']
            test_output.append(f"{test_row['content']}（{'，'.join(diagnosis_content) if not diagnosis_content.empty else '无'}）")
        else:
            test_output.append(test_row['content'])
    test_output = '\n'.join(test_output) or "无"

    # 创建输出文件路径
    base_name = os.path.basename(file_path)
    output_file = os.path.join(output_folder, base_name.replace('.xlsx', '.txt'))
    
    # 写入到 txt 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{patient_info}\n{medical_history}\n{prior_diagnosis}\n{prior_treatment}\n{main_problem}\n\n")
        f.write(f"【评论区诊断】：\n{diagnosis_output}\n")
        f.write(f"【治疗方案】：\n{treatment_output}\n")
        f.write(f"【检查建议】：\n{test_output}\n")

def process_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 查找所有 Excel 文件
    excel_files = glob.glob(os.path.join(input_folder, '*.xlsx'))
    
    for file_path in excel_files:
        process_excel(file_path, output_folder)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_folder> <output_folder>")
    else:
        input_folder = sys.argv[1]
        output_folder = sys.argv[2]
        process_folder(input_folder, output_folder)
