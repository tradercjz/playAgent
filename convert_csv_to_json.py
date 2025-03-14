import csv
import json
import os

def convert_csv_to_json(csv_file_path, output_file_path=None):
    """
    读取CSV文件并将每行转换为JSON结构
    
    Args:
        csv_file_path: CSV文件路径
        output_file_path: 输出JSON文件路径，如果为None则不保存文件
        
    Returns:
        list: 包含所有行的JSON对象列表
    """
    # 存储所有行的JSON对象
    all_rows = []

    encodings = ['utf-8', 'gbk', 'utf-16', 'latin-1', 
                'big5', 'shift_jis', 'euc-jp', 'iso-8859-1',
                'cp1252', 'ascii']
    
    for encoding in encodings:
        try:
            with open(csv_file_path, 'r', encoding=encoding) as csv_file:
                # 创建CSV读取器
                csv_reader = csv.DictReader(csv_file)
                
                # 遍历每一行
                for row in csv_reader:
                    # 将行数据添加到列表中
                    all_rows.append(dict(row))
                    print(row)
                    
            # 如果指定了输出文件路径，则保存JSON文件
                if output_file_path:
                    with open(output_file_path, 'w', encoding='utf-8') as json_file:
                        json.dump(all_rows, json_file, ensure_ascii=False, indent=2)
                    print(f"已将数据保存到 {output_file_path}")
                        
                return all_rows
        except UnicodeDecodeError:
            continue
        except Exception as e:
                # Log other errors but continue trying other encodings
                continue
    
    

def display_json_sample(json_data, num_samples=3):
    """
    展示JSON数据的样本
    
    Args:
        json_data: JSON数据列表
        num_samples: 要展示的样本数量
    """
    if not json_data:
        print("没有数据可展示")
        return
        
    print(f"\n共转换 {len(json_data)} 条记录。以下是前 {min(num_samples, len(json_data))} 条记录的JSON格式：\n")
    
    for i, item in enumerate(json_data[:num_samples]):
        print(f"记录 {i+1}:")
        print(json.dumps(item, ensure_ascii=False, indent=2))
        print()

def main():

    csv_file_path = "./askQA.csv"
    output_file_path = "./jsonQA.csv"
    json_data = convert_csv_to_json(csv_file_path, output_file_path)
    
    # 展示样本数据
    display_json_sample(json_data)

if __name__ == "__main__":
    main()
