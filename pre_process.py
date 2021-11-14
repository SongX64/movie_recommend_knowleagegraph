import json
import re

import pandas as pd


def Netflix(MAX_USER=1000):
    # ↑ MAX_USER定义参数，读取前多少个用户

    # 声明集合
    # d_movie 用作 电影id-titile 的映射
    d_movie = dict()
    s_movie = set()

    # 1.读取电影标题写入文件，先写个标题行
    out_movies = open("datasets_out/out_movies.csv", "w", encoding="utf-8")
    out_movies.write("title\n")

    # 按行读取
    for line in open("datasets/movie_titles.csv", "r", encoding='ISO-8859-1'):
        # 数据格式：电影ID，上映年份，电影名称
        # 数据格式示例：1,2003,Dinosaur Planet
        line = line.strip().split(',')

        movie_id = int(line[0])
        # 电影标题去掉原来引号，并在两边加上双引号，变为 "Dinosaur Planet"
        title = line[2].replace("\"", "")
        title = "\"" + title + "\""

        # 字典，类似于HashMap，key-value格式
        # 电影字典 d_movie 存储：电影ID　——　电影名称
        d_movie[movie_id] = title

        # 为啥验重
        if title in s_movie:
            continue

        # set,类似于HashSet
        # 存储电影标题？
        s_movie.add(title)
        out_movies.write(f"{title}\n")

    out_movies.close()

    # 2.读取评分写入文件，先写个标题行
    out_grade = open("datasets_out/out_grade.csv", "w", encoding="utf-8")
    out_grade.write("user_id,title,grade\n")

    # 文件集合，讲道理是可以读取多个的，然后针对每个文件进行循环处理
    # 电脑卡的话就只用第一个就行
    files = {"datasets/combined_data_1.txt",
             "datasets/combined_data_2.txt",
             "datasets/combined_data_3.txt",
             "datasets/combined_data_4.txt"}

    # 数据格式：
    # 电影ID:
    # 用户ID，用户评分，评分日期

    # 数据格式示例：
    # 1:
    # 1488844,3,2005-09-06

    for f in files:
        movie_id = -1
        # 读当前文件
        for line in open(f, "r"):
            # 查找分号，若找到就是电影ID行，否自就是用户评分行
            pos = line.find(":")

            # 找到了分号，说明是电影ID行
            if pos != -1:
                movie_id = int(line[:pos])
                continue

            # 未找到分号，说明是用户评分行
            line = line.strip().split(",")
            user_id = int(line[0])
            rating = int(line[1])

            if user_id > MAX_USER:
                continue

            print(f"{user_id},{d_movie[movie_id]},{rating}")
            out_grade.write(f"{user_id},{d_movie[movie_id]},{rating}\n")

    out_grade.close()


def TMDB():
    # 正则匹配
    pattern = re.compile("[A-Za-z0-9]+")

    # 电影数据集中，提取 类型 关键字 制片人 几个关键属性
    out_genre = open("datasets_out/out_genre.csv", "w", encoding="utf-8")
    out_genre.write("title,genre\n")
    out_keyword = open("datasets_out/out_keyword.csv", "w", encoding="utf-8")
    out_keyword.write("title,keyword\n")
    out_productor = open("datasets_out/out_productor.csv", "w", encoding="utf-8")
    out_productor.write("title,productor\n")

    # 读取电影信息
    # 数据格式：行头，json行
    # budget,genres,homepage,id,keywords,original_language,original_title,overview,popularity,production_companies,production_countries,release_date,revenue,runtime,spoken_languages,status,tagline,title,vote_average,vote_count
    # 237000000,"[{""id"": 28, ""name"": ""Action""}, {""id"": 12, ""name"": ""Adventure""}, {""id"": 14, ""name"": ""Fantasy""}, {""id"": 878, ""name"": ""Science Fiction""}]",http://www.avatarmovie.com/,19995,"[{""id"": 1463, ""name"": ""culture clash""}, {""id"": 2964, ""name"": ""future""}, {""id"": 3386, ""name"": ""space war""}, {""id"": 3388, ""name"": ""space colony""}, {""id"": 3679, ""name"": ""society""}, {""id"": 3801, ""name"": ""space travel""}, {""id"": 9685, ""name"": ""futuristic""}, {""id"": 9840, ""name"": ""romance""}, {""id"": 9882, ""name"": ""space""}, {""id"": 9951, ""name"": ""alien""}, {""id"": 10148, ""name"": ""tribe""}, {""id"": 10158, ""name"": ""alien planet""}, {""id"": 10987, ""name"": ""cgi""}, {""id"": 11399, ""name"": ""marine""}, {""id"": 13065, ""name"": ""soldier""}, {""id"": 14643, ""name"": ""battle""}, {""id"": 14720, ""name"": ""love affair""}, {""id"": 165431, ""name"": ""anti war""}, {""id"": 193554, ""name"": ""power relations""}, {""id"": 206690, ""name"": ""mind and soul""}, {""id"": 209714, ""name"": ""3d""}]",en,Avatar,"In the 22nd century, a paraplegic Marine is dispatched to the moon Pandora on a unique mission, but becomes torn between following orders and protecting an alien civilization.",150.437577,"[{""name"": ""Ingenious Film Partners"", ""id"": 289}, {""name"": ""Twentieth Century Fox Film Corporation"", ""id"": 306}, {""name"": ""Dune Entertainment"", ""id"": 444}, {""name"": ""Lightstorm Entertainment"", ""id"": 574}]","[{""iso_3166_1"": ""US"", ""name"": ""United States of America""}, {""iso_3166_1"": ""GB"", ""name"": ""United Kingdom""}]",2009-12-10,2787965087,162,"[{""iso_639_1"": ""en"", ""name"": ""English""}, {""iso_639_1"": ""es"", ""name"": ""Espa\u00f1ol""}]",Released,Enter the World of Pandora.,Avatar,7.2,11800

    # pandas会自动读取标题行，读取后为 DataFrame 对象
    df = pd.read_csv("datasets/tmdb_5000_movies.csv", sep=",")

    # 标记一下哪几行是json格式的字符串
    json_columns = {'genres', 'keywords', 'production_companies'}

    # 将json格式字符串加载出来
    for column in json_columns:
        df[column] = df[column].apply(json.loads)

    # 提取需要的几行
    df = df[{'genres', 'keywords', "original_title", 'production_companies'}]
    for _, row in df.iterrows():
        # 匹配一下题目，如果有奇奇怪怪符号的电影就给去掉？
        title = row["original_title"]
        if not pattern.fullmatch(title):
            continue
        title = "\"" + title + "\""

        # 从DataFrame中读取数据，直接类似于arrays的形式get到
        for g in row["genres"]:
            genre = g["name"]
            genre = "\"" + genre + "\""
            print(f"{title},{genre}")
            out_genre.write(f"{title},{genre}\n")
        for k in row["keywords"]:
            keyword = k["name"]
            keyword = "\"" + keyword + "\""
            print(f"{title},{keyword}")
            out_keyword.write(f"{title},{keyword}\n")
        for p in row["production_companies"]:
            productor = p["name"]
            productor = "\"" + productor + "\""
            print(f"{title},{productor}")
            out_productor.write(f"{title},{productor}\n")

    out_productor.close()
    out_keyword.close()
    out_genre.close()


if __name__ == "__main__":
    Netflix()
    TMDB()
