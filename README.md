# 电影推荐系统Demo

根据视频教程：[基于知识图谱电影推荐问答系统实战_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1aU4y1g7hw)

手撸了一个，简单的Demo，学习一下 Python 和 Neo4j 的简单使用。

## 环境

- python3.7
- neo4j-3.5.6
- PyChram 2021

## 数据集

- [Netflix Prize data -- combined_data_1.txt | Kaggle](https://www.kaggle.com/netflix-inc/netflix-prize-data?select=combined_data_1.txt)
- [TMDB 5000 Movie Dataset | Kaggle](https://www.kaggle.com/tmdb/tmdb-movie-metadata)

## 文件结构

- datasets：存放数据集的文件夹(其中 Netflix数据集 过大没有上传)
- datasets_out：存放数据预处理结果的文件夹，也就是运行 `pre_process.py` 后输出的结果文件
- main.py：推荐模块
- pre_process.py：数据预处理模块