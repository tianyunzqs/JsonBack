# -*- coding: utf-8 -*-
# @Description :

import collections
import json
import csv
import io
from typing import List, Dict, Any, Union
import pandas as pd


def recurrence_combine(data_list: List[Dict]) -> List[Dict]:
    """
    利用递归对数据集进行合并
    :param data_list:
    :return:
    """
    if not data_list:
        return []

    if len(data_list) > 1:
        # 删除全为None的行
        items = [item for item in data_list if list(filter(None, list(item.values())))]
        if not items:
            return []
    else:
        items = [item for item in data_list]

    all_columns = list(items[0].keys())
    # if len(all_columns) == 1:
    #     items = [{all_columns[0]: v} for v in set([item[all_columns[0]] for item in items])]
    flag = True   # data_list是否可以合并
    split_idx = (0, 0)
    for i, col in enumerate(all_columns):
        col_val_counter = collections.Counter([item[col] for item in items if item[col]])
        col_val_counter_len = len(col_val_counter)
        if col_val_counter_len == len(items):
            return items
        if col_val_counter_len >= 2:
            flag = False
            if len(items) == 2:
                return items
        split_idx = max(split_idx, (col_val_counter_len, i))

    if flag:  # items可以合并
        combine_result = {key: None for key in items[0].keys()}
        for _item in items:
            for key, value in _item.items():
                if not combine_result[key]:
                    combine_result[key] = value
        return [combine_result]

    result = []
    col = all_columns[split_idx[1]]  # 自动选择分割列
    first_no_col = None
    sub_items = collections.defaultdict(list)
    for i, item in enumerate(items):
        if not first_no_col and item[col]:
            first_no_col = item[col]
        sub_items[item[col]].append({k: v for k, v in item.items() if k != col})

    # 如果划分列为None，则直接把None划分列的数据添加至第一个子集（同时需要满足字段相等或包含）
    for special_token in [None, ""]:
        if special_token in sub_items and first_no_col:
            special_items = sub_items.pop(special_token)
            for special_item in special_items:
                should_combine = True
                for k, v in special_item.items():
                    if v not in set([t[k] for t in sub_items[first_no_col]] + [special_token]):
                        should_combine = False
                        break
                if should_combine:
                    sub_items[first_no_col].append(special_item)
                else:
                    sub_items[special_token].append(special_item)

    for col_val, sub_item in sub_items.items():
        sub_res = recurrence_combine(sub_item)
        for r in sub_res:
            tmp = {col: col_val}
            tmp.update(r)
            if tmp not in result:
                result.append(tmp)
        # print(len(result))
    return result


def parse_file_content(file_content: bytes, file_name: str) -> List[Dict[str, Any]]:
    """
    解析上传的文件内容，支持多种格式
    
    Args:
        file_content: 文件内容（字节格式）
        file_name: 文件名
        
    Returns:
        解析后的数据列表
        
    Raises:
        ValueError: 不支持的文件格式或解析错误
    """
    file_extension = file_name.split('.')[-1]
    try:
        if file_extension in ['json', 'jsonl']:
            return parse_json_file(file_content)
        elif file_extension in ['csv']:
            return parse_csv_file(file_content)
        elif file_extension in ['xlsx', 'xls']:
            return parse_excel_file(file_content)
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
    except Exception as e:
        raise ValueError(f"文件解析失败: {str(e)}")


def parse_json_file(file_content: bytes) -> List[Dict[str, Any]]:
    """解析JSON文件、解析JSONL文件（每行一个JSON对象）"""
    try:
        content = file_content.decode('utf-8')
    except Exception as e:
        raise ValueError(f"文件解析失败: {str(e)}")

    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # 如果是单个对象，转换为列表
            return [data]
        else:
            raise ValueError("JSON文件必须包含对象或对象数组")
    except json.JSONDecodeError as e:
        try:
            lines = content.strip().split('\n')
            result = []
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line:  # 跳过空行
                    try:
                        obj = json.loads(line)
                        if isinstance(obj, dict):
                            result.append(obj)
                        else:
                            raise ValueError(f"第{line_num}行不是有效的JSON对象")
                    except json.JSONDecodeError as e:
                        raise ValueError(f"第{line_num}行JSON格式错误: {str(e)}")

            return result
        except Exception as e:
            raise ValueError(f"JSONL文件解析失败: {str(e)}")


def parse_csv_file(file_content: bytes) -> List[Dict]:
    """解析CSV文件"""
    try:
        content = file_content.decode('utf-8')
        df = pd.read_csv(io.BytesIO(file_content))
        df.drop_duplicates(inplace=True)
        result = [{k: None if pd.isna(v) else v for k, v in dd.items()} for dd in df.to_dict(orient='records')]
        return result
    except Exception as e:
        raise ValueError(f"CSV文件解析失败: {str(e)}")


def parse_excel_file(file_content: bytes) -> List[Dict]:
    """解析Excel文件"""
    try:
        # 使用pandas读取Excel文件
        df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
        df.drop_duplicates(inplace=True)
        result = [{k: None if pd.isna(v) else v for k, v in dd.items()} for dd in df.to_dict(orient='records')]
        return result
    except Exception as e:
        raise ValueError(f"Excel文件解析失败: {str(e)}")
