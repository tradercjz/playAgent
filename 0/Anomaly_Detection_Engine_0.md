Prompt:
在DolphinDB中，如何配置createAnomalyDetectionEngine函数以实现同时检测温度超过65和超过前一窗口75%分位数的双指标异常检测？请说明metrics参数的具体写法及窗口参数设置要求。
Input:
Answer:


Prompt:
在DolphinDB中如何配置createAnomalyDetectionEngine函数来实现同时检测温度超过65和超过前一窗口75%分位数的双指标异常检测？请具体说明metrics参数的元代码写法以及窗口参数windowSize和step的设置要求。

Input:
Function Name:
createAnomalyDetectionEngine

在DolphinDB中，要实现同时检测温度超过65和超过前一窗口75%分位数的双指标异常检测，需要以下配置：

1. metrics参数应使用元代码格式编写：
```python
<[temp > 65, temp > percentile(temp, 75)]>
```

2. 窗口参数设置要求：
- 必须指定windowSize（窗口长度）和step（窗口移动步长），因第二个指标包含聚合函数percentile
- 示例设置为windowSize=6（单位与时间列精度一致，如毫秒），step=3
- 窗口对齐规则按时间类型自动处理，如TIMESTAMP类型按alignmentSize规整

3. 完整函数调用示例：
```python
engine = createAnomalyDetectionEngine(
    name="engine1",
    metrics=<[temp > 65, temp > percentile(temp, 75)]>,
    dummyTable=sensor,
    outputTable=outputTable,
    timeColumn=`time,
    keyColumn=,          # 无分组时留空
    windowSize=6,        # 窗口长度6个时间单位
    step=3               # 窗口步进3个时间单位
)
```

这种配置下，引擎会同时进行实时单值检测（第一条指标）和基于窗口聚合值的检测（第二条指标），当温度突破任一阈值时触发异常记录到输出表。
R1 CoT:
嗯，用户问的是如何在DolphinDB中使用createAnomalyDetectionEngine函数配置双指标异常检测，特别是温度超过65和超过前一窗口75%分位数的情况。我需要先回忆一下文档里的相关内容。

首先，记得createAnomalyDetectionEngine的metrics参数需要元代码，用尖括号包裹多个表达式。比如，文档里的例子用了<[temp > 65, temp > percentile(temp, 75)]>。所以用户的问题中，两个指标应该这样写。

接下来是窗口参数的设置。因为第二个指标用了聚合函数percentile，所以必须指定windowSize和step。文档中提到，当指标包含聚合函数时，必须设置这两个参数。比如应用场景中的例子，窗口长度是6毫秒，步长3毫秒。用户的问题中，假设窗口长度和步长需要根据具体需求设置，但需要符合数据窗口的规则，比如窗口长度和步长的单位要与时间列的数据类型匹配。

另外，输出表的结构也要注意，时间列在前，然后是分组列（如果有的话），接着是异常类型和内容。用户的问题中没有分组列，所以输出表的结构是时间、anomalyType和anomalyString。

还要注意，当指标中包含聚合和非聚合列时，引擎会在窗口移动时计算聚合值，并用最近窗口的结果与当前数据比较。例如，第二个指标会在每个窗口计算75%分位数，然后新数据到达时比较。

总结一下，用户需要的是metrics参数的写法以及windowSize和step的设置。正确的示例应该像文档中的例子那样，用尖括号包含两个表达式，并正确设置窗口参数，如windowSize和step的值，比如6和3。同时，确保输出表的结构正确，并且订阅流数据表时使用append!函数将数据传入引擎。

Correct CoT:
嗯，用户问的是如何在DolphinDB中使用createAnomalyDetectionEngine函数配置双指标异常检测，特别是温度超过65和超过前一窗口75%分位数的情况。我需要先回忆一下文档里的相关内容。

首先，记得createAnomalyDetectionEngine的metrics参数需要元代码，用尖括号包裹多个表达式。比如，文档里的例子用了<[temp > 65, temp > percentile(temp, 75)]>。所以用户的问题中，两个指标应该这样写。

接下来是窗口参数的设置。因为第二个指标用了聚合函数percentile，所以必须指定windowSize和step。文档中提到，当指标包含聚合函数时，必须设置这两个参数。比如应用场景中的例子，窗口长度是6毫秒，步长3毫秒。用户的问题中，假设窗口长度和步长需要根据具体需求设置，但需要符合数据窗口的规则，比如窗口长度和步长的单位要与时间列的数据类型匹配。

另外，输出表的结构也要注意，时间列在前，然后是分组列（如果有的话），接着是异常类型和内容。用户的问题中没有分组列，所以输出表的结构是时间、anomalyType和anomalyString。

还要注意，当指标中包含聚合和非聚合列时，引擎会在窗口移动时计算聚合值，并用最近窗口的结果与当前数据比较。例如，第二个指标会在每个窗口计算75%分位数，然后新数据到达时比较。

总结一下，用户需要的是metrics参数的写法以及windowSize和step的设置。正确的示例应该像文档中的例子那样，用尖括号包含两个表达式，并正确设置窗口参数，如windowSize和step的值，比如6和3。同时，确保输出表的结构正确，并且订阅流数据表时使用append!函数将数据传入引擎。

Function Name:
createAnomalyDetectionEngine
