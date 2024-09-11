import pandas as pd
import sys
import os

def load_annotations(file_path):
    return pd.read_excel(file_path)

def overlap(span1, span2):
    return not (span1[1] < span2[0] or span1[0] > span2[1])

def compare_annotations(annotations1, annotations2, tolerance=5):
    results = {
        'label_count_difference': 0,
        'label_count_total': 0,
        'precision': 0,
        'recall': 0,
        'f1': 0,
        'diagnosis_val_precision': 0,
        'diagnosis_val_recall': 0,
        'diagnosis_val_f1': 0,
    }

    # Label counts
    label_counts1 = annotations1['label'].value_counts().to_dict()
    label_counts2 = annotations2['label'].value_counts().to_dict()
    all_labels = set(label_counts1.keys()).union(set(label_counts2.keys()))
    
    for label in all_labels:
        count1 = label_counts1.get(label, 0)
        count2 = label_counts2.get(label, 0)
        results['label_count_difference'] += abs(count1 - count2)
        results['label_count_total'] += max(count1, count2)
    
    # Preparing to calculate precision, recall, and F1
    label_true_positives = {}
    label_false_positives = {}
    label_false_negatives = {}
    
    # Initialize dictionaries
    for label in all_labels:
        label_true_positives[label] = 0
        label_false_positives[label] = 0
        label_false_negatives[label] = 0

    # Compare annotations
    for index1, row1 in annotations1.iterrows():
        span1 = (row1['span_start'], row1['span_end'])
        label1 = row1['label']
        val1 = row1['Val']
        event1 = row1['event']
        
        matched = False
        for index2, row2 in annotations2.iterrows():
            span2 = (row2['span_start'], row2['span_end'])
            label2 = row2['label']
            val2 = row2['Val']
            event2 = row2['event']
            
            if overlap(span1, span2):
                matched = True
                if label1 == label2:
                    label_true_positives[label1] += 1
                else:
                    label_false_positives[label2] += 1
        
        if not matched:
            label_false_negatives[label1] += 1
    
    # Calculate precision, recall, and F1
    for label in all_labels:
        tp = label_true_positives[label]
        fp = label_false_positives[label]
        fn = label_false_negatives[label]
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        results['precision'] += precision
        results['recall'] += recall
        results['f1'] += f1

    # Calculate diagnosis_val scores
    diagnosis1 = annotations1[annotations1['label'] == 'Diagnosis']
    diagnosis2 = annotations2[annotations2['label'] == 'Diagnosis']
    
    val_true_positives = 0
    val_false_positives = 0
    val_false_negatives = 0
    
    for index1, row1 in diagnosis1.iterrows():
        val1 = row1['Val']
        id1 = row1['turn_id']
        
        match = diagnosis2[(diagnosis2['turn_id'] == id1)]
        if not match.empty:
            val2 = match['Val'].values[0]
            if (val1 in ['present', 'hypothetical_present'] and val2 in ['present', 'hypothetical_present']) or \
               (val1 in ['negated', 'hypothetical_negated'] and val2 in ['negated', 'hypothetical_negated']):
                val_true_positives += 1
            else:
                val_false_positives += 1
        else:
            val_false_negatives += 1
    
    diagnosis_val_precision = val_true_positives / (val_true_positives + val_false_positives) if (val_true_positives + val_false_positives) > 0 else 0
    diagnosis_val_recall = val_true_positives / (val_true_positives + val_false_negatives) if (val_true_positives + val_false_negatives) > 0 else 0
    diagnosis_val_f1 = 2 * diagnosis_val_precision * diagnosis_val_recall / (diagnosis_val_precision + diagnosis_val_recall) if (diagnosis_val_precision + diagnosis_val_recall) > 0 else 0
    
    results['precision'] /= len(all_labels)
    results['recall'] /= len(all_labels)
    results['f1'] /= len(all_labels)
    
    results['diagnosis_val_precision'] = diagnosis_val_precision
    results['diagnosis_val_recall'] = diagnosis_val_recall
    results['diagnosis_val_f1'] = diagnosis_val_f1
    
    return results

def save_results(results, file_path, data_idx):
    # Create a DataFrame from the results
    df_results = pd.DataFrame([{
        'data_index': data_idx,
        'annotation1_label_total': results['label_count_total'],
        'label_num_diff': results['label_count_difference'],
        'precision': results['precision'],
        'recall': results['recall'],
        'f1': results['f1'],
        'diagnosis_val_precision': results['diagnosis_val_precision'],
        'diagnosis_val_recall': results['diagnosis_val_recall'],
        'diagnosis_val_f1': results['diagnosis_val_f1']
    }])
    
    if os.path.exists(file_path):
        # If file exists, append the new results
        df_existing = pd.read_excel(file_path)
        df_combined = pd.concat([df_existing, df_results], ignore_index=True)
        df_combined.to_excel(file_path, index=False)
    else:
        # If file does not exist, create it
        df_results.to_excel(file_path, index=False)

def print_results(results, file1, file2):
    print(f'Comparison between {file1} and {file2}:')
    print(f'  Precision: {results["precision"]:.2%}')
    print(f'  Recall: {results["recall"]:.2%}')
    print(f'  F1 Score: {results["f1"]:.2%}')
    print(f'  Diagnosis Value Precision: {results["diagnosis_val_precision"]:.2%}')
    print(f'  Diagnosis Value Recall: {results["diagnosis_val_recall"]:.2%}')
    print(f'  Diagnosis Value F1 Score: {results["diagnosis_val_f1"]:.2%}')

def main(file1, file2, output_file):
    annotations1 = load_annotations(file1)
    annotations2 = load_annotations(file2)
    data_idx = os.path.splitext(os.path.basename(file1))[0]
    
    results = compare_annotations(annotations1, annotations2)
    print_results(results, file1, file2)
    save_results(results, output_file, data_idx)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python compare_annotations.py <file1.xlsx> <file2.xlsx> <output_file.xlsx>")
    else:
        file1 = sys.argv[1]
        file2 = sys.argv[2]
        output_file = sys.argv[3]
        main(file1, file2, output_file)
