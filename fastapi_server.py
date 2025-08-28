# -*- coding: utf-8 -*-
# @Description :

import os
import sys
import time
import json
import argparse
import traceback
import uvicorn
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi import APIRouter, Request, FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
from json_assistant.json_utils import recurrence_combine, parse_file_content


# 创建FastAPI应用
app = FastAPI(
    title="TyJson工具箱 - FastAPI版本",
    description="JSON合并服务，提供高性能的JSON数据处理接口",
    version="1.0.0"
)
# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境请限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MergeRequest(BaseModel):
    datasets: List[Dict[str, Any]]


class MergeResponse(BaseModel):
    success: bool
    msg_error: str = ""
    data: List[Dict[str, Any]]
    summary: Dict[str, Any]


class HealthResponse(BaseModel):
    success: bool
    message: str
    timestamp: str


@app.post("/api/merge", response_model=MergeResponse)
async def merge_datasets(request: MergeRequest):
    """
    JSON合并接口
    
    接收多个JSON数据集，使用递归算法进行智能合并
    """
    try:
        all_data = request.datasets
        
        if not all_data:
            raise HTTPException(status_code=400, detail="请提供有效的数据集数组")

        if len(all_data) == 0:
            raise HTTPException(status_code=400, detail="没有可合并的数据")

        # 验证数据结构
        if not all(isinstance(item, dict) and item is not None for item in all_data):
            raise HTTPException(status_code=400, detail="数据集必须包含对象元素")

        # 执行合并
        result = recurrence_combine(all_data)
        
        # 生成摘要信息
        summary = {
            "inputRecords": len(all_data),
            "outputRecords": len(result),
            "columns": list(result[0].keys()) if result else []
        }
        
        return MergeResponse(
            success=True,
            data=result,
            summary=summary
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"合并失败: {error}")
        raise HTTPException(status_code=500, detail=f"合并失败: {str(error)}")


@app.post("/api/merge-with-file", response_model=MergeResponse)
async def merge_with_file(files: List[UploadFile] = File(...)):
    """文件与JSON数据合并接口"""
    try:
        all_data = []
        
        # 处理上传的文件
        for file in files:
            file_name = file.filename.lower() if file.filename is not None else ""
            file_content = await file.read()
            file_data = parse_file_content(file_content, file_name)
            all_data.extend(file_data)
        
        if not all_data:
            raise HTTPException(status_code=400, detail="请提供有效的数据集数组")

        if len(all_data) == 0:
            raise HTTPException(status_code=400, detail="没有可合并的数据")

        # 验证数据结构
        if not all(isinstance(item, dict) and item is not None for item in all_data):
            raise HTTPException(status_code=400, detail="数据集必须包含对象元素")

        # 执行合并
        result = recurrence_combine(all_data)
        
        # 生成摘要信息
        summary = {
            "inputRecords": len(all_data),
            "outputRecords": len(result),
            "columns": list(result[0].keys()) if result else []
        }
        
        return MergeResponse(
            success=True,
            data=result,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as error:
        print(f"合并失败: {error}")
        raise HTTPException(status_code=500, detail=f"合并失败: {str(error)}")


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查接口
    
    用于检查服务是否正常运行
    """
    return HealthResponse(
        success=True,
        message="JSON合并服务运行正常",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.get("/")
async def root():
    """
    根路径接口
    
    返回服务基本信息
    """
    return {
        "service": "TyJson工具箱 - FastAPI版本",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "merge": "/api/merge",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    print("🚀 启动TyJson工具箱 - FastAPI版本")
    print("📍 服务地址: http://localhost:3001")
    print("🔗 合并接口: http://localhost:3001/api/merge")
    print("💚 健康检查: http://localhost:3001/api/health")
    print("📚 API文档: http://localhost:3001/docs")
    print("📊 支持跨域访问")
    
    uvicorn.run(
        "__main__:app",
        host="0.0.0.0",
        port=3001,
        reload=True,
        log_level="info"
    )
