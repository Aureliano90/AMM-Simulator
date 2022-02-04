import pymongo


class Record:
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient['OKEx']

    def __init__(self, col=''):
        self.mycol = self.mydb[col]

    def find_last(self, match: dict):
        """返回最后一条记录

        :param match: 匹配条件
        :rtype: dict
        """
        pipeline = [{'$match': match},
                    {'$sort': {'_id': -1}},
                    {'$limit': 1}]
        for x in self.mycol.aggregate(pipeline):
            return x

    def insert(self, match: dict):
        """插入对应记录

        :param match: 匹配条件
        """
        self.mycol.insert_one(match)

    def delete(self, match: dict):
        """删除对应记录

        :param match: 匹配条件
        """
        self.mycol.delete_one(match)
