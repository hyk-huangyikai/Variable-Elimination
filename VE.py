class VariableElimination():
    @staticmethod
    def inference(factor_list, query_variables,
                  ordered_list_of_hidden_variables, evidence_list):
        #给每个证据变量赋予指定的值
        for ev in evidence_list:
            #遍历所有变量结点
            for i in range(len(factor_list)):
                #如果该变量结点涉及证据变量，则更新其值域
                if ev in factor_list[i].var_list:
                    factor_list[i] = factor_list[i].restrict(ev,evidence_list[ev])
        #遍历消除每个剩余变量
        for var in ordered_list_of_hidden_variables:
            #生层新的变量结点集
            new_factor_list = [x for x in factor_list]
            #将原变量结点集清空
            factor_list = []
            first = 0
            #遍历新的变量结点集
            for i in range(len(new_factor_list)):
                #如果此时结点中的变量已经被赋值，则将其加入到factor_list
                if len(new_factor_list[i].var_list) == 0:
                    factor_list.append(new_factor_list[i])
                    continue
                #如果消除变量存在因子结点中的变量集，并且第一次出现，则进行下一步
                if var in new_factor_list[i].var_list and first == 0:
                    multi_res = new_factor_list[i] #赋值给第一个乘数
                    first += 1  
                #如果消除变量在因子结点中的变量集，并且不是第一次出现，进入下面步骤
                elif var in new_factor_list[i].var_list and first != 0:
                    #将当前因子结点与multi_res进行相乘
                    multi_res = multi_res.multiply(new_factor_list[i])
                #否则将其加入到factor_list
                else:
                    factor_list.append(new_factor_list[i])
            #最后消除当前变量var，得到新的结点
            new_factor = multi_res.sum_out(var)
            #将生成的新因子结点放入factor_list，进入下一轮变量消除
            factor_list.append(new_factor)

        #最后将剩余的因子结点相乘，归一化，打印生成的结果
        print("RESULT: ")
        res = factor_list[0]
        for factor in factor_list[1:]:
            res = res.multiply(factor)
        total = sum(res.cpt.values())
        res.cpt = {k: v / total for k, v in res.cpt.items()}
        res.print_inf()

    @staticmethod
    def print_factors(factor_list):
        for factor in factor_list:
            factor.print_inf()


class Util:
    @staticmethod
    def to_binary(num, len):
        return format(num, '0' + str(len) + 'b')


class Node():
    def __init__(self, name, var_list):
        self.name = name
        self.var_list = var_list
        self.cpt = {}

    def set_cpt(self, cpt):
        self.cpt = cpt

    def print_inf(self):
        print("Name = " + self.name)
        print(" vars " + str(self.var_list))
        for key in self.cpt:
            print("   key: " + key + " val : " + str(self.cpt[key]))
        print()

    #因子结点相乘
    def multiply(self, factor):
        '''function that multiplies with another factor'''
        #初始化变量
        new_cpt = {}
        same_index1 = 0  
        same_index2 = 0
        #定位两个因子结点相同变量在各自变量列表的下标
        for i in range(len(self.var_list)):
            if self.var_list[i] in factor.var_list:
                same_index1 = i
                same_index2 = factor.var_list.index(self.var_list[i])
        #遍历因子结点1的cpt
        for key1 in self.cpt:
            #对于每一个key1，遍历结点2的cpt
            for key2 in factor.cpt:
                #如果key1和key2在相同变量的对应位置取值相同，则可以相乘
                if key1[same_index1] == key2[same_index2]:
                    #去掉相同变量
                    new_key1 = key1[:same_index1] + key1[same_index1+1:]
                    new_key2 = key2
                    #取两者变量的并集
                    new_key = new_key1 + new_key2
                    #将相乘的结果放入新生成的字典new_cpt
                    new_cpt[new_key] = self.cpt[key1] * factor.cpt[key2]
        #合并两者的变量列表
        new_list = self.var_list + factor.var_list
        #删除多余的相同变量
        new_list.pop(same_index1)
        #生成新结点
        new_node = Node('f' + str(new_list), new_list)
        #初始化值域字典
        new_node.set_cpt(new_cpt)
        return new_node

    #消除指定变量的影响
    def sum_out(self, variable):
        '''function that sums out a variable given a factor'''
        #初始化
        new_var_list = []
        new_cpt = {}
        #定位指定变量在变量列表的下标
        index = self.var_list.index(variable)
        #遍历结点的所有值域
        for key in self.cpt:
            #将key中指定变量的位置去除
            new_key = key[:index] + key[index+1:]
            #如果新字典new_cpt已经有new_key键值，累加，否则创建新键值
            if new_key in new_cpt:
                new_cpt[new_key] += self.cpt[key]
            else:
                new_cpt[new_key] = self.cpt[key]
        #复制变量列表
        new_var_list = self.var_list[:]
        #去除指定变量
        new_var_list.remove(variable)
        #创建新结点
        new_node = Node('f' + str(new_var_list), new_var_list)
        #初始化值域字典
        new_node.set_cpt(new_cpt)
        return new_node

    #在指定变量的特定值条件下更新结点的值域
    def restrict(self, variable, value):
        '''function that restricts a variable to some value
        in a given factor'''
        #定位指定变量在变量列表的下标
        index = self.var_list.index(variable)
        #新值域字典
        new_cpt = {}
        #遍历当前所有值域
        for key in self.cpt:
            #如果key在指定变量位置上的取值为特定值，则将
            #该值域和概率放入新字典
            if key[index] == str(value):
                new_cpt[key] = self.cpt[key]
        #复制变量列表
        new_var_list = self.var_list[:]
        #生成新结点
        new_node = Node('f' + str(new_var_list), new_var_list)
        #初始化值域字典
        new_node.set_cpt(new_cpt)
        return new_node




# Create nodes for Bayes Net
B = Node('B', ['B'])
E = Node('E', ['E'])
A = Node('A', ['A', 'B', 'E'])
J = Node('J', ['J', 'A'])
M = Node('M', ['M', 'A'])

# Generate cpt for each node
B.set_cpt({'0': 0.999, '1': 0.001})
E.set_cpt({'0': 0.998, '1': 0.002})
A.set_cpt({'111': 0.95, '011': 0.05, '110': 0.94, '010': 0.06,
           '101':0.29, '001': 0.71, '100': 0.001, '000': 0.999})
J.set_cpt({'11': 0.9, '01': 0.1, '10': 0.05, '00': 0.95})
M.set_cpt({'11': 0.7, '01': 0.3, '10': 0.01, '00': 0.99})

print("P(A) **********************")
VariableElimination.inference([B, E, A, J, M], ['A'], ['B', 'E', 'J', 'M'], {})

print("P(J && ~M) ************************")
VariableElimination.inference([B, E, A, J, M], ['J','M'], ['B', 'E', 'A'], {})

print("P(A | J, ~M) **********************")
VariableElimination.inference([B, E, A, J, M], ['A'], ['B', 'E'], {'J':1, 'M':0})

print("P(B | A) **********************")
VariableElimination.inference([B, E, A, J, M], ['B'], ['E', 'J','M'], {'A':1})

print("P(B | J, ~M) **********************")
VariableElimination.inference([B, E, A, J, M], ['B'], ['E', 'A'], {'J':1, 'M':0})

print("P(J&&~M | ~B) **********************")
VariableElimination.inference([B, E, A, J, M], ['J','M'], ['E', 'A'], {'B':0})

