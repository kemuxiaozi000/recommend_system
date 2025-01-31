# -*-coding:utf-8-*-

"""
    Author: Thinkgamer
    Desc:
        代码4-10 实现基于二分-Kmeans的商品价格聚类
"""
import numpy as np
import pandas as pd
import random

class kMeans:
    def __init__(self):
        pass

    # 加载数据集
    def loadData(self,file):
        return pd.read_csv(file,header=0,sep=",")

    # 去除异常值,使用正态分布方法,同时保证最大异常值为5000，最小异常值为1
    def filterAnomalyValue(self,data):
        upper = np.mean(data["price"]) + 3 * np.std(data["price"])
        lower = np.mean(data["price"]) - 3 * np.std(data["price"])
        upper_limit = upper if upper > 5000 else 5000
        lower_limit = lower if lower > 1 else 1
        print("最大异常值为:{}，最小异常值为:{}"
              .format(upper_limit,lower_limit))
        # 过滤掉大于最大异常值和小于最小异常值的
        newData = data[(data["price"]<upper_limit)
                       & (data["price"]>lower_limit)]
        return newData,upper_limit,lower_limit

    # 初始化簇类中心
    def initCenters(self,values,K,Cluster):
        random.seed(100)
        oldCenters = list()
        for i in range(K):
            index = random.randint(0,len(values))
            Cluster.setdefault(i,{})
            Cluster[i]["center"]=values[index]
            Cluster[i]["values"]=[]

            oldCenters.append(values[index])
        return oldCenters,Cluster

    # 计算任意两条数据之间的欧式距离
    def distance(self,price1,price2):
        return np.emath.sqrt(pow(price1-price2, 2))

    # 聚类
    def kMeans(self,data,K,maxIters):
        Cluster = dict() # 最终聚类结果
        oldCenters,Cluster = self.initCenters(data,K,Cluster)
        # print("初始的簇类中心为:{}".format(oldCenters))
        # 标志变量，若为True，则继续迭代
        clusterChanged = True
        i = 0  # 记录迭代次数 最大迭代
        while clusterChanged:
            for price in data:
                # 每条数据距离离最近簇类的距离，初始化为正无穷大
                minDistance = np.inf
                # 每条数据对应的索引，初始化为-1
                minIndex = -1
                for key in Cluster.keys():
                    # 计算每条数据到簇类中心的距离
                    dis = self.distance(price, Cluster[key]["center"])
                    if dis < minDistance:
                        minDistance = dis
                        minIndex = key
                Cluster[minIndex]["values"].append(price)

            newCenters = list()
            for key in Cluster.keys():
                newCenter = np.mean(Cluster[key]["values"])
                Cluster[key]["center"] = newCenter
                newCenters.append(newCenter)
            # print("第{}次迭代后的簇类中心为:{}".format(i,newCenters))
            if oldCenters == newCenters or i > maxIters:
                clusterChanged = False
            else:
                oldCenters = newCenters
                i += 1
                # 删除self.Cluster 中记录的簇类值
                for key in Cluster.keys(): Cluster[key]["values"]=[]
        return Cluster

    # 计算对应的SSE值
    def SSE(self,data,mean):
        newData = np.mat(data)-mean
        return (newData * newData.T).tolist()[0][0]

    # 二分kMeans
    def diKMeans(self,data,K=7):
        clusterSSEResult = dict() # 簇类对应的SSE值
        clusterSSEResult.setdefault(0,{})
        clusterSSEResult[0]["values"] = data
        clusterSSEResult[0]["sse"] = np.inf  # inf为正无穷大
        clusterSSEResult[0]["center"] = np.mean(data)

        while len(clusterSSEResult) < K:
            maxSSE = -np.inf
            maxSSEKey = 0
            # 找到最大SSE值对应数据，进行kmeans聚类
            for key in clusterSSEResult.keys():
                if clusterSSEResult[key]["sse"] > maxSSE:
                    maxSSE = clusterSSEResult[key]["sse"]
                    maxSSEKey = key
            # clusterResult {0: {'center': x, 'values': []}, 1: {'center': x, 'values': []}}
            clusterResult = \
                self.kMeans(clusterSSEResult[maxSSEKey]["values"],K=2,maxIters = 200)

            # 删除clusterSSE中的minKey对应的值
            del clusterSSEResult[maxSSEKey]
            # 将经过kMeas聚类后的结果赋值给clusterSSEResult
            clusterSSEResult.setdefault(maxSSEKey,{})
            clusterSSEResult[maxSSEKey]["center"]=clusterResult[0]["center"]
            clusterSSEResult[maxSSEKey]["values"]=clusterResult[0]["values"]
            clusterSSEResult[maxSSEKey]["sse"]=\
                self.SSE(clusterResult[0]["values"],clusterResult[0]["center"])

            maxKey = max(clusterSSEResult.keys()) + 1
            clusterSSEResult.setdefault(maxKey,{})
            clusterSSEResult[maxKey]["center"]=clusterResult[1]["center"]
            clusterSSEResult[maxKey]["values"]=clusterResult[1]["values"]
            clusterSSEResult[maxKey]["sse"]=\
                self.SSE(clusterResult[1]["values"],clusterResult[1]["center"])

        return clusterSSEResult

if __name__ == "__main__":
    file = "../data/sku-price/skuid_price.csv"
    km = kMeans()
    data = km.loadData(file)
    newData,upper_limit,lower_limit = km.filterAnomalyValue(data)
    # Cluster = km.kMeans(newData["price"].values,K=7,maxIters=200)
    # print(Cluster)
    clusterSSE = km.diKMeans(newData["price"].values,K=7)
    print(clusterSSE)
