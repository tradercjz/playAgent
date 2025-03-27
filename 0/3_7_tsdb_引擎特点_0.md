Prompt:
在 DolphinDB 中，如何为存储几百几千列的宽表创建使用 TSDB 引擎的数据库表？请说明具体使用的函数及参数配置。
Input:
Answer:


在 DolphinDB 中为宽表创建 TSDB 引擎数据库表的步骤如下：

1. **使用关键函数**：
   ```python
   db = database(directory="dfs://wideDB", partitionType=HASH, partitionScheme=[STRING, 10], engine="TSDB")
   ```

2. **参数配置要点**：
   - `engine` 必须设为 "TSDB"
   - 宽表需要显式定义所有列名及类型：
   ```python
   schema = table(1:0, 3000#`col, 3000#INT) // 示例3000列整型宽表
   ```

3. **创建分区表**：
   ```python
   wideTable = db.createPartitionedTable(
       table=schema,
       tableName="wideTbl",
       partitionColumns=`col, // 选择合适的分区列
       sortColumns=`col_time  // 必须指定时间或设备类排序列
   )
   ```

4. **重要注意事项**：
   - 建议配置 `sortKeyMappingFunction=[hashBucket,100]` 处理高并发写入
   - 对超宽表（>1000列）需增加配置：
   ```python
   config(setting, TSDBMaxColumnCount=5000) // 修改最大列数限制
   ```

该配置充分利用 TSDB 的列式存储和二级索引特性，可有效支持数千列宽表的高效读写。
R1 CoT:
好的，我需要回答用户关于如何在DolphinDB中为宽表创建使用TSDB引擎的数据库表的问题。首先，我需要回顾用户提供的文档内容。文档提到TSDB引擎适合存储几百几千列的宽表，以及其他适用场景。接下来，用户询问具体的函数和参数配置。

我记得在DolphinDB中，创建数据库表通常使用`database`和`createPartitionedTable`函数。对于TSDB引擎，关键点在于建库时的engine参数和建表时的字段配置。文档中提到TSDB适合宽表，所以可能需要指定sortColumns，并且处理大量列的情况。

首先，创建数据库时应使用`database`函数，并设置engine为'TSDB'。然后，创建表时，使用`createPartitionedTable`，需要指定表的结构，包括所有列名和类型。对于宽表，可能需要指定sortColumns参数来优化查询性能，通常选择时间列作为排序键。此外，确保分区方案合理，比如按时间分区，以配合TSDB的优势。

还需要注意，TSDB支持数据去重和更新，因此在配置参数时可能需要设置keepDuplicates参数，例如设为ALL表示保留所有数据，或者根据需求调整。另外，如果表中有复杂类型如array vector或BLOB，也需要在定义表结构时正确指定类型。

总结步骤：使用`database`函数创建TSDB引擎的数据库，设置分区方式和engine参数。然后使用`createPartitionedTable`定义表结构，指定sortColumns为时间列，并配置其他参数如keepDuplicates。需要确保列数多的宽表正确配置，以利用TSDB的优势。

Correct CoT:
好的，我需要回答用户关于如何在DolphinDB中为宽表创建使用TSDB引擎的数据库表的问题。首先，我需要回顾用户提供的文档内容。文档提到TSDB引擎适合存储几百几千列的宽表，以及其他适用场景。接下来，用户询问具体的函数和参数配置。

我记得在DolphinDB中，创建数据库表通常使用`database`和`createPartitionedTable`函数。对于TSDB引擎，关键点在于建库时的engine参数和建表时的字段配置。文档中提到TSDB适合宽表，所以可能需要指定sortColumns，并且处理大量列的情况。

首先，创建数据库时应使用`database`函数，并设置engine为'TSDB'。然后，创建表时，使用`createPartitionedTable`，需要指定表的结构，包括所有列名和类型。对于宽表，可能需要指定sortColumns参数来优化查询性能，通常选择时间列作为排序键。此外，确保分区方案合理，比如按时间分区，以配合TSDB的优势。

还需要注意，TSDB支持数据去重和更新，因此在配置参数时可能需要设置keepDuplicates参数，例如设为ALL表示保留所有数据，或者根据需求调整。另外，如果表中有复杂类型如array vector或BLOB，也需要在定义表结构时正确指定类型。

总结步骤：使用`database`函数创建TSDB引擎的数据库，设置分区方式和engine参数。然后使用`createPartitionedTable`定义表结构，指定sortColumns为时间列，并配置其他参数如keepDuplicates。需要确保列数多的宽表正确配置，以利用TSDB的优势。

Function Name:
createPartitionedTable
