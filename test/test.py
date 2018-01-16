# 分类
import torch
import torch.nn.functional as F
from torch.autograd import Variable
import matplotlib.pyplot as plt

# 假数据
n_data = torch.ones(100, 2)  # 都是 1 的数据，100行2列
x0 = torch.normal(2 * n_data, 1)  # 类型0 x data (tensor), shape=(100, 2)
y0 = torch.zeros(100)  # 类型0 y data (tensor), shape=(100, 1)
x1 = torch.normal(-2 * n_data, 1)  # 类型1 x data (tensor), shape=(100, 2)
y1 = torch.ones(100)  # 类型1 y data (tensor), shape=(100, 1)
x2 = torch.normal(4 * n_data, 1)
y2 = torch.ones(100) + torch.ones(100)

# 注意 x, y 数据的数据形式是一定要像下面一样 (torch.cat 是在合并数据)
# x：数据点，y：颜色值
x = torch.cat((x0, x1, x2)).type(torch.FloatTensor)  # FloatTensor = 32-bit floating
y = torch.cat((y0, y1, y2)).type(torch.LongTensor)  # LongTensor = 64-bit integer

# torch 只能在 Variable 上训练, 所以把它们变成 Variable
x, y = Variable(x), Variable(y)


# 画图
# plt.scatter(x.data.numpy()[:, 0], x.data.numpy()[:, 1], c=y.data.numpy())
# plt.show()


# 建立神经网络
# 建立一个神经网络我们可以直接运用 torch 中的体系.
# 先定义所有的层属性(__init__()), 然后再一层层搭建(forward(x))层于层的关系链接.
# 建立关系的时候, 我们会用到激励函数
class Net(torch.nn.Module):  # 继承 torch 的 Module
    def __init__(self, n_feature, n_hidden, n_output):
        super(Net, self).__init__()  # 继承 __init__ 功能
        # 定义每层用什么样的形式
        self.hidden = torch.nn.Linear(n_feature, n_hidden)  # 隐藏层线性输出
        self.predict = torch.nn.Linear(n_hidden, n_output)  # 输出层线性输出

    def forward(self, x):  # 这同时也是 Module 中的 forward 功能
        # 正向传播输入值, 神经网络分析出输出值
        x = F.relu(self.hidden(x))  # 激励函数(隐藏层的线性值)
        x = self.predict(x)  # 输出值
        return x


# 几个类别就几个 output
net = Net(n_feature=2, n_hidden=30, n_output=3)

optimizer = torch.optim.SGD(net.parameters(), lr=0.1)
# 交叉熵损失函数
loss_func = torch.nn.CrossEntropyLoss()

for t in range(200):
    prediction = net(x)
    # prediction 是二维的，y 是一维的
    loss = loss_func(prediction, y)
    optimizer.zero_grad()  # 清空上一步的残余更新参数值
    loss.backward()  # 误差反向传播, 计算参数更新值
    optimizer.step()  # 将参数更新值施加到 net 的 parameters 上

    # 可视化
    if t % 2 == 0:
        # 清空内容
        plt.cla()
        # 取 prediction 每一维中最大的数，的索引值
        prediction = torch.max(prediction, 1)[1]
        pred_y = prediction.data.numpy()
        target_y = y.data.numpy()
        plt.scatter(x.data.numpy()[:, 0], x.data.numpy()[:, 1], c=pred_y)
        # 预测值与真实值相同的个数的总和
        sum_y = sum(pred_y == target_y)
        accuracy = sum_y / 300  # 预测中有多少和真实值一样
        plt.text(1.5, -4, 'Accuracy=%.2f\nt=%d' % (accuracy, t))
        if t == 198:
            plt.text(0, 0, 'done')
        plt.pause(0.1)

plt.show()
