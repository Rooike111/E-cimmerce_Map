from neo4j import GraphDatabase
from pymysql.cursors import DictCursor

from configuration.config import *
import pymysql

from neo4j_driver import driver


# 读取MySQL工具类
class MysqlReader:
    def __init__(self):
        self.connection = pymysql.connect(
            **MYSQL_CONFIG,
        )
        self.cursor = self.connection.cursor(DictCursor)

    # 查询Mysql，读取数据
    def read(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    # 关闭链接
    def close(self):
        self.cursor.close()
        self.connection.close()


class Neo4jWriter:
    def __init__(self):
        self.driver = GraphDatabase.driver(**NEO4j_CONFIG)

    def write_node(self, label:str,properties:list[dict]):
        """
        写入节点（批量，固定标签）
        :param properties:
        :param label:
        :return:
        """
        cypher = f"""
                UNWIND $batch AS item
                MERGE (:{label} {{id:item.id,name:item.name}})
            """
        self.driver.execute_query(cypher,batch=properties)

    def write_relation(self, rl_type:str,start_label:str,end_label:str,batch:list[dict]):
        """
        写入关系
        """
        cypher = f"""
                    UNWIND $batch AS item
                    MATCH (start:{start_label}{{id:item.start_id}}),(end:{end_label}{{id:item.end_id}})
                    MERGE (start)-[:{rl_type}]->(end)
                """
        self.driver.execute_query(cypher, batch=batch)

if __name__ == '__main__':
    reader = MysqlReader()
    writer = Neo4jWriter()
    # 1.读取Category1
    sql = "select id,name from base_category1"
    category1 = reader.read(sql)
    writer.write_node("Category1",category1)
    # 读取Category2
    sql = "select id,name from base_category2"
    category2 = reader.read(sql)
    writer.write_node("Category2", category2)
    # # 3.Category2-[Belong]->Category1
    sql = "select id as start_id,category1_id as end_id from base_category2"
    relations = reader.read(sql)
    writer.write_relation("Belong",start_label="Category2",end_label="Category1",batch=relations)
