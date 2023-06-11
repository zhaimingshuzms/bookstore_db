# bookstore
[![Build Status](https://travis-ci.com/DaSE-DBMS/bookstore.svg?branch=master)](https://travis-ci.com/DaSE-DBMS/bookstore)
[![codecov](https://codecov.io/gh/DaSE-DBMS/bookstore/branch/master/graph/badge.svg)](https://codecov.io/gh/DaSE-DBMS/bookstore)


## 功能

实现一个提供网上购书功能的网站后端。<br>
网站支持书商在上面开商店，购买者可以通过网站购买。<br>
买家和卖家都可以注册自己的账号。<br>
一个卖家可以开一个或多个网上商店，
买家可以为自已的账户充值，在任意商店购买图书。<br>
支持 下单->付款->发货->收货 流程。<br>

1.实现对应接口的功能，见项目的doc文件夹下面的.md文件描述 （60%）<br>

其中包括：

1)用户权限接口，如注册、登录、登出、注销<br>

2)买家用户接口，如充值、下单、付款<br>

3)卖家用户接口，如创建店铺、填加书籍信息及描述、增加库存<br>

通过对应的功能测试，所有test case都pass <br>


2.为项目添加其它功能 ：（40%）<br>

1)实现后续的流程 <br>
发货 -> 收货

增加seller接口 mark_order_shipped finish
增加buyer接口 mark_order_received finish

2)搜索图书 <br>
用户可以通过关键字搜索，参数化的搜索方式；
如搜索范围包括，题目，标签，目录，内容；全站搜索或是当前店铺搜索。
如果显示结果较大，需要分页
(使用全文索引优化查找)

3)订单状态，订单查询和取消订单<br>
用户可以查自已的历史订单，用户也可以取消订单。<br>
取消订单可由买家主动地取消订单，或者买家下单后，经过一段时间超时仍未付款，订单也会自动取消。 <br>

给订单增加时间戳
buyer增加查询订单的操作 finish
buyer增加取消订单操作 finish (需要退回库存)
给订单增加订单状态 (unpaid,paid,delivered,Canceled,Finished) 订单完成后不可取消  finish

## bookstore目录结构
```
bookstore
  |-- be                            后端
        |-- model                     后端逻辑代码
        |-- view                      访问后端接口
        |-- ....
  |-- doc                           JSON API规范说明
  |-- fe                            前端访问与测试代码
        |-- access
        |-- bench                     效率测试
        |-- data
            |-- book.db                 sqlite 数据库(book.db，较少量的测试数据)
            |-- book_lx.db              sqlite 数据库(book_lx.db， 较大量的测试数据，要从网盘下载)
            |-- scraper.py              从豆瓣爬取的图书信息数据的代码
        |-- test                      功能性测试（包含对前60%功能的测试，不要修改已有的文件，可以提pull request或bug）
        |-- conf.py                   测试参数，修改这个文件以适应自己的需要
        |-- conftest.py               pytest初始化配置，修改这个文件以适应自己的需要
        |-- ....
  |-- ....
```


## 安装配置
安装python (需要python3.6以上)


进入bookstore文件夹下：

安装依赖

    pip install -r requirements.txt

执行测试

    bash script/test.sh

（注意：如果提示"RuntimeError: Not running with the Werkzeug Server"，请输入下述命令，将flask和Werkzeug的版本均降低为2.0.0。

    pip install flask==2.0.0
    pip install Werkzeug==2.0.0

## 要求

2～3人一组，做好分工，完成下述内容：

1.bookstore文件夹是该项目的demo，采用flask后端框架与sqlite数据库，实现了前60%功能以及对应的测试用例代码。
要求大家创建本地MongoDB数据库，将bookstore/fe/data/book.db中的内容以合适的形式存入本地数据库


书本的内容可自行构造一批，也可参从网盘下载，下载地址为：

    https://pan.baidu.com/s/1bjCOW8Z5N_ClcqU54Pdt8g

提取码：

    hj6q

2.在完成前60%功能的基础上，继续实现后40%功能，要有接口、后端逻辑实现、数据库操作、代码测试。对所有接口都要写test case，通过测试并计算测试覆盖率（尽量提高测试覆盖率）。

3.尽量使用索引，对程序与数据库执行的性能有考量

4.尽量使用git等版本管理工具

5.不需要实现界面，只需通过代码测试体现功能与正确性


## 报告内容

1.每位组员的学号、姓名，以及分工

2.文档数据库设计：文档schema

3.对60%基础功能和40%附加功能的接口、后端逻辑、数据库操作、测试用例进行介绍，展示测试结果与测试覆盖率。

4.如果完成，可以展示本次大作业的亮点，比如要求中的“3 4”两点。

注：验收依据为报告，本次大作业所作的工作要完整展示在报告中。


## 验收与考核准测

- 提交 **代码+报告** 压缩包到 **作业提交入口**
- 命名规则：2023_SJTU_PJ1_第几组(.zip)
- 提交截止日期：**2023.4.22 23:59**

考核标准：

1. 没有提交或没有实质的工作，得D
2. 完成"要求"中的第点，可得C
3. 完成前3点，通过全部测试用例且有较高的测试覆盖率，可得B
4. 完成前2点的基础上，体现出第3 4点，可得A
5. 以上均为参考，最后等级会根据最终的工作质量有所调整
