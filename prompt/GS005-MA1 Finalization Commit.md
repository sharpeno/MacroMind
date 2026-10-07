执行一次 **GS005-MA1 Finalization Commit**。

本任务不是重新迁移GS005，不重新抽取视频，不重新生成Claim/Argument/MethodSignal。

只处理三个已经完成外部人工裁决的Review：

- MA1-C005
- MA1-MR01
- MA1-MR03

## 1. 输入

使用：

```
golden_sample_005.ma1_candidate.json
```

首先复制为：

```
golden_sample_005.ma1_candidate.pre_finalization.json
```

不得覆盖原候选文件。

## 2. MA1-C005裁决

人工裁决：

```
keep_scenario_only
```

依据：

C005的表达是：

“如果中国保持当前进步速度，很快会超过美国。”

该表达包含未来结果，但主播没有明确选择或认可“当前进步速度会保持”这个条件，因此没有形成branch selection forecast。

不得因为low resolvability本身排除Forecast。

处理：

- C005本身保持不变。
- SC01继续作为Scenario。
- `forecast_admitted = false`
- `admission_reason = "condition_not_endorsed_no_branch_selection"`
- `resolvability = "low"`，如Schema已有对应字段则写入；没有则只保存在Review/annotation，不新增核心字段。

更新Review `MA1-C005`：

```
status: resolved
decision: keep_scenario_only
requires_human: false
blocks_verified_promotion: false
```

如果C005当前位于：

```
machine_use_policy.immutable_object_quarantine
```

则从该列表移除。

不得创建新的Forecast对象。

## 3. MA1-MR01裁决

人工裁决：

```
accept_migrated_uncertain
```

MR01由于GS001只有摘要，无法验证具体方法步骤或原句。

要求：

```
match_type: uncertain
match_status: uncertain
```

如果当前已经如此，不重复改对象。

更新Review：

```
status: resolved
decision: accept_migrated_uncertain
requires_human: false
blocks_verified_promotion: false
```

保留所有legacy值与migration provenance。

## 4. MA1-MR03裁决

人工裁决：

```
accept_migrated_uncertain
```

“追问执行条件”仍过于宽泛，不能据此认定与旧方法存在partial/exact recurrence。

要求：

```
match_type: uncertain
match_status: uncertain
```

如果当前已经如此，不重复改对象。

更新Review：

```
status: resolved
decision: accept_migrated_uncertain
requires_human: false
blocks_verified_promotion: false
```

## 5. Finalization Metadata

新增：

```
finalization:
  version: GS005-MA1-FINALIZATION-1
  resolved_reviews:
    - MA1-C005
    - MA1-MR01
    - MA1-MR03
  human_decisions:
    MA1-C005: keep_scenario_only
    MA1-MR01: accept_migrated_uncertain
    MA1-MR03: accept_migrated_uncertain
  semantic_objects_regenerated: false
  claim_ids_changed: false
  argument_ids_changed: false
```

加入实际执行时间戳。

## 6. MA.1状态更新

将：

```
ma1_compliance:
  migrated_local_validation_pass_manual_review_pending
```

更新为：

```
ma1_compliance:
  migrated_local_validation_pass_human_accepted
```

将：

```
human_acceptance: true
```

Golden状态更新为：

```
golden_status:
  ma1_migration_accepted_knowledge_review_pending
```

仍必须保持：

```
frozen: false
```

仍必须保持：

```
production_import_ready: false
```

因为这次只接受MA.1 migration，不代表所有知识Review已经完成，也不代表Core Ontology正式Freeze。

## 7. 不得修改

不得：

- 重新生成任何Claim。
- 重新生成Argument。
- 修改Claim ID / Argument ID / MethodSignal ID。
- 自动解决原RQ01–RQ37。
- 将unknown改成verified。
- 将Warning强制清零。
- 将GS005标记frozen。
- 将production_import_ready改成true。
- 将本次Finalization解释为Core Ontology Freeze批准。

## 8. Validator

运行与上一次完全相同的MA.1 Validator。

输出：

```
validation_after_finalization.json
```

验收硬条件：

```
ERROR = 0
```

Warning允许存在。

预计Warning数可能减少约3条，但Warning总数不是硬指标。

额外检查：

- MA1-C005 = resolved
- MA1-MR01 = resolved
- MA1-MR03 = resolved
- C005不再位于immutable_object_quarantine
- production_import_ready仍为false
- frozen仍为false

## 9. 输出文件

生成：

- `golden_sample_005.ma1_accepted.json`
- `finalization/finalization_log.json`
- `finalization/validation_after_finalization.json`
- `finalization/finalization_diff.md`

## 10. finalization_diff.md

仅列：

1. Resolved Reviews
2. Changed Fields
3. Removed Quarantine Objects
4. Unchanged Safety / Governance State
5. Validator Result
6. Remaining Warning Count
7. Final Golden Status

## 11. 最终报告

最后只报告：

```
Finalization completed: yes/no
Validator ERROR:
Validator WARNING:
Three adjudicated reviews resolved: yes/no
C005 forecast decision:
C005 removed from quarantine: yes/no
production_import_ready:
frozen:
MA.1 migration status:
Remaining manual reviews:
```

不要宣布Core Ontology正式Freeze。