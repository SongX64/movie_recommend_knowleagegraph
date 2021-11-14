import pandas as pd
from neo4j import GraphDatabase

# 连接数据库驱动
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "zxcv1234!"))

# 参数设置
k = 10  # 考虑最相似的用户，也就是最邻近的邻居
moives_common = 3  # 考虑用户相似度，要有多少个电影公共看过
usesrs_common = 2  # 至少共通看过2个电影，说用户相似
threshold_sim = 0.9  # 用户相似度阈值


def load_data():
    with driver.session() as session:
        # 清空数据库
        session.run("""MATCH ()-[r]->() DELETE r""")
        session.run("""MATCH (n) DETACH DELETE n""")

        # --------------从文件中读取数据,存入 neo4j 数据库中------------
        # 加载电影
        print("Loading movies ...")
        session.run("""
            LOAD CSV WITH HEADERS FROM "file:///out_movies.csv" AS csv
            CREATE (:Movie {title: csv.title})
        """)

        # 加载评分
        print("Loading gradings ... ")
        session.run("""
            LOAD CSV WITH HEADERS FROM "file:///out_grade.csv" AS csv
            MERGE(m:Movie {title: csv.title})
            MERGE(u:User {id: toInteger(csv.user_id)})
            CREATE (u)-[:RATED {grading: toInteger(csv.grade)}]->(m)
        """)

        # 加载电影类型
        print("Loading genre ...")
        session.run("""
            LOAD CSV WITH HEADERS FROM "file:///out_genre.csv" AS csv
            MERGE (m:Movie {title: csv.title})
            MERGE (g:Genre {genre: csv.genre})
            CREATE (m)-[:HAS_GENRE]->(g)
        """)

        # 加载关键词
        print("Loading keywords ...")
        session.run("""
            LOAD CSV WITH HEADERS FROM "file:///out_keyword.csv" AS csv
            MERGE(m:Movie {title: csv.title})
            MERGE(k:Keyword {keyword: csv.keyword})
            CREATE (m)-[:HAS_KEYWORD]->(k)
        """)

        # 加载导演
        print("Loading productors ...")
        session.run("""
            LOAD CSV WITH HEADERS FROM "file:///out_productor.csv" AS csv
            MERGE(m:Movie {title: csv.title})
            MERGE(p:Productor {name: csv.productor})
            CREATE (m)-[:HAS_PRODUCTOR]->(p)
        """)
        # -------------------读取文件完毕-------------------------


def queries():
    while True:
        userid = int(input("请输入要为哪位用户推荐电影，输入ID即可："))
        m = int(input("为该用户推荐的电影个数："))

        # 电影类型
        genre = []
        if int(input("是否排除类型？输入0或1:")):
            # 排除的话
            with driver.session() as session:
                try:
                    # 查询所有类型,放入元组中
                    q = session.run(f"""MATCH (g:Genre) RETURN g.genre AS genre""")
                    result = []
                    for i, r in enumerate(q):
                        result.append(r["genre"])

                    # 将 genre 列转为 DataFrame 类型，并列出提示
                    df = pd.DataFrame(result, columns=["genre"])
                    print()
                    print(df)

                    # 根据上面的输出，输入类型
                    inp = input("请输入喜欢的类型，例如 1 2 3 ：")
                    if len(inp) != 0:
                        inp = inp.split(" ")
                        # TODO 这里是什么意思? lamuda表达式 ???
                        genre = [df["genre"].iloc[int(x)] for x in inp]
                finally:
                    print("Error")

        # 进行查询, 用户u1对电影的评分, 降序排序
        with driver.session() as session:
            q = session.run(f"""
                MATCH (u1:User {{ id:{userid} }})-[r:RATED]-(m:Movie)
                RETURN m.title AS title,r.grading AS grade
                ORDER BY grade DESC
            """)
            print()
            print("你评分过的电影如下所示: ")

            # 将 session 查询结果放入元组中
            result = []
            for r in q:
                result.append([r["title"], r["grade"]])

            # 输出结果, 用户对于电影的一个评分列表
            if len(result) == 0:
                print("没有结果推荐")
            else:
                df = pd.DataFrame(result, columns=["title", "grade"])
                print()
                print(df.to_string(index=True))
            print("---------------------------------------------------------------------------------------------------")

            # 删除用户相似性关系
            session.run(f"""
                MATCH (u1:User)-[s:SIMILARITY]-(u2:User)
                DELETE s
            """)

            # 重新计算用户相似性
            # 通过电影连接两个用户, u1 --rated-- movie --rated-- u2
            # 计算u1,u2共同评论过的电影,然后根据两个人的评分来计算相似度
            # (用户1评分 * 用户2评分)的总和,除以他们分别的根号平方和
            session.run(f"""
                MATCH (u1:User {{id : {userid}}})-[r1:RATED]-(m:Movie)-[r2:RATED]-(u2:User)
                WITH
                    u1, u2,
                    COUNT(m) AS movies_common,
                    SUM(r1.grading * r2.grading)/(SQRT( SUM(r1.grading^2) ) * SQRT( SUM(r2.grading^2) )) as sim
                WHERE movies_common >= {moives_common} AND sim > {threshold_sim}
                MERGE (u1)-[s:SIMILARITY]-(u2)
                SET s.sim = sim
            """)

            # 条件语句拼装, 过滤类型
            Q_GENRE = ""
            if len(genre) > 0:
                Q_GENRE = "AND ((SIZE(gen) > 0) AND "
                Q_GENRE += "(ANY(X IN " + str(genre) + " WHERE X IN gen))"
                Q_GENRE += ")"

            q = session.run(f"""
                MATCH (u1:User{{id : {userid}}})-[s:SIMILARITY]-(u2:User)
                WITH u1,u2,s
                ORDER BY s.sim DESC LIMIT {k}
                MATCH (m:Movie)-[r:RATED]-(u2)
                OPTIONAL MATCH (g:Genre)--(m)
                WITH u1,u2,s,m,r, COLLECT(DISTINCT g.genre) AS gen
                WHERE NOT((m)-[:RATED]-(u1)) {Q_GENRE}
                WITH
                    m.title AS title,
                    SUM(r.grading * s.sim)/SUM(s.sim) AS grade,
                    COUNT(u2) AS num,
                    gen
                WHERE num >= {usesrs_common}
                RETURN title,grade,num,gen
                ORDER BY grade DESC, num DESC
                LIMIT {m}
            """)

            print("推荐的电影:")
            result = []
            for r in q:
                result.append([r["title"], r["grade"], r["num"], r["gen"]])
            if len(result) == 0:
                print("无推荐")
                print()
                continue
            df = pd.DataFrame(result, columns=["title", "avg grade", "num recommenders", "genre"])
            print()
            print(df.to_string(index=True))
            print("---------------------------------------------------------------------------------------------------")


if __name__ == "__main__":
    if int(input("是否需要重新加载知识图谱? 输入0或1: ")):
        load_data()
    queries()
