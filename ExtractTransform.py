import pymysql
from collections import Counter


class ExtractTransformer(object):
    data = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
            conn = pymysql.connect(host='localhost', user='root', passwd='123456', db='django_movie', port=3306)
            cursor = conn.cursor()  # 连接数据库及光标
            cursor.execute('select * from doubanmovie')
            cls.data = cls.__pre_process(cursor.fetchall())
            cls.actor_counter = cls.__count_actor()
            cls.director_counter = cls.__count_director()
            cls.type_count = cls.__count_type()
            cls.country_count = cls.__count_country()
            cls.year_counter_by_type = cls.__count_year_by_type()
            cls.decades_counter = cls.__count_decades()
        return cls._instance

    @classmethod
    def __pre_process(cls, src_data):
        try:
            return [{"name": i[1], "director": i[2], "actor": i[3].split(' / '), "type": i[4].split('/'),
                     "country": i[5].split(' / '), "time": i[6][2:11], "duration": i[7].split('分钟')[0], "score": i[8]}
                    for i in src_data]
        except Exception as e:
            return None

    @classmethod
    def __count_actor(cls):
        c = Counter()
        for i in cls.data:
            c.update(i['actor'])
        return c.most_common(10)

    @classmethod
    def __count_director(cls):
        c = Counter()
        for i in cls.data:
            c.update([i['director']])
        return c.most_common(10)

    @classmethod
    def __count_type(cls):
        c = Counter()
        for i in cls.data:
            c.update(i['type'])
        return c

    @classmethod
    def __count_country(cls):
        c = Counter()
        for i in cls.data:
            c.update(i['country'])
        return c

    @classmethod
    def __count_decades(cls):
        c_li = {i: Counter() for i in
                ['剧情', '喜剧', '爱情', '冒险', '奇幻', '犯罪', '动画', '惊悚', '动作', '悬疑', '家庭', '科幻', '传记',
                 '战争']}
        for i in cls.data:
            [c_li[t].update([i['time'][:3]]) for t in i['type'] if
             t in ['剧情', '喜剧', '爱情', '冒险', '奇幻', '犯罪', '动画', '惊悚', '动作', '悬疑', '家庭', '科幻',
                   '传记',
                   '战争']]
        c = Counter()
        c.update([i['time'][:3] for i in cls.data])
        c_li['全部'] = c
        for t in c_li.keys():
            c_li[t] = list(zip(*sorted([(k + '0', c_li[t].get(k, 0)) for k in list(c.keys())])))
        return c_li

    @classmethod
    def __count_year_by_type(cls):
        c_li = {i: Counter() for i in
                ['剧情', '喜剧', '爱情', '冒险', '奇幻', '犯罪', '动画']}
        for i in cls.data:
            [c_li[t].update([i['time'][:4]]) for t in i['type'] if
             t in ['剧情', '喜剧', '爱情', '冒险', '奇幻', '犯罪', '动画']]
        c = Counter()
        c.update([i['time'][:4] for i in cls.data])
        c_li['全部'] = c

        for t in c_li.keys():
            c_li[t] = list(zip(*sorted([(k, c_li[t].get(k, 0)) for k in list(c.keys())])))
        return c_li


if __name__ == '__main__':
    print(ExtractTransformer().country_count)
    print(ExtractTransformer().type_count)
    print(ExtractTransformer().actor_counter)
    print(ExtractTransformer().director_counter)
    print(ExtractTransformer().decades_counter)

    print(ExtractTransformer().year_counter_by_type)

    # print([i[0] for i in ExtractTransformer().type_count.most_common(14)])
