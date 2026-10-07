执行 **GS005-MA1 Finalization Hotfix 1.1**。

本任务不是重新执行Migration，不重新抽取任何视频，不重新生成任何Claim、Argument、Forecast、Scenario、MethodSignal或MR，也不重新裁决MA1-C005、MA1-MR01、MA1-MR03。

当前状态：

```
Finalization-1:
ERROR   = 4
WARNING = 69
PASS    = 1801
```

4个ERROR全部来自C005：

```
R062
V-MA108
R060
V-MA106
```

原因是：

Finalization-1根据人工裁决关闭了MA1-C005并将C005移出quarantine，但C005在此前Migration中因为open-review exemption而没有补齐MA.1 canonical fields。

此次只进行确定性的Schema normalization。

------

# 1. 输入

读取：

```
golden_sample_005.ma1_accepted.json
```

首先备份：

```
golden_sample_005.ma1_accepted.json
→
golden_sample_005.ma1_accepted.pre_hotfix_1_1.json
```

不得覆盖已有Finalization-1历史记录。

------

# 2. C005唯一允许的对象修改

定位：

```
claim_id = C005
```

不得改变：

```
statement
claim_type
derivation_type
temporal_mode
source_segment
reasoner_id
analysis_context
review_refs
任何原始历史语义
```

只补齐MA.1 canonical schema fields。

将：

```
comparison_basis:
  comparison_type: null
  baseline_period: null
  baseline_value: null
  delta_value: null
  delta_unit: null
```

规范化为：

```
comparison_basis:
  comparison_type: unknown
  baseline_period: null
  baseline_value: null
  baseline_source_ref: null
  delta_value: null
  delta_unit: null
```

将：

```
semantic_role: null
```

改为：

```
semantic_role: unknown
```

增加：

```
recognition_stage: unknown
```

这些值是Schema normalization，不是新的事实判断。

不得根据文本猜测更具体的semantic_role、recognition_stage或comparison baseline。

------

# 3. 移除C005特殊Schema豁免

当前：

```
ma1_migration:
  immutable_review_exceptions:
    C005: ...
```

删除C005这一exception。

如果删除后：

```
immutable_review_exceptions:
```