# uuidgen

终端 UUID 生成器：默认 v4，一条命令拿到 v1 / v3 / v5 / v7。纯标准库、纯本地。

## 安装

零依赖，Python 3.10+：

```bash
cd uuidgen
python3 -m uuidgen
```

## 用法

```bash
uuidgen                                  # 一个 v4
uuidgen --count 5                        # 5 个 v4
uuidgen --v1                             # 时间+节点版本
uuidgen --v7                             # 时间排序版本（数据库主键友好）
uuidgen --v5 --namespace dns --name example.com
uuidgen --v3 --namespace url --name https://example.com/x
uuidgen --no-dashes                      # 32 位 hex，无连字符
uuidgen --upper --count 3                # 大写
```

## 输出示例

```
$ uuidgen --count 3
3f6a9c2e-1b4d-4f8a-9e2c-5d7b1a3f4e6c
a1b2c3d4-5678-4abc-8def-0123456789ab
9d8c7b6a-5432-4fed-9cba-9876543210fe

$ uuidgen --v3 --namespace dns --name www.example.com
5df41881-3aed-3515-88a7-2f4a814cf09e   # RFC 4122 附录 B 的已知向量
```

## 各版本说明

| 版本 | 来源 | 特点 |
|---|---|---|
| v1 | 时间 + MAC/随机节点 | 时间排序，但可能泄露机器信息 |
| v3 | MD5(命名空间 + 名字) | 确定性；MD5 已弱化，只做标识不用做安全 |
| v4 | 122 位随机 | 默认，最常用 |
| v5 | SHA-1(命名空间 + 名字) | 确定性；推荐替代 v3 |
| v7 | 48 位毫秒时间戳 + 74 位随机 | 时间排序 + 不泄露机器信息，适合做数据库主键 |

## 诚实说明

- **v7 是手工实现的**：Python 3.12 的标准库没有 `uuid.uuid7`（3.14 才加入），本工具按 RFC 9562 第 5.7 节手工构造：48 位 Unix 毫秒时间戳 + 4 位版本号(`0111`) + 12 位随机 + 2 位 variant(`10`) + 62 位随机。版式与标准库未来的 `uuid7()` 完全兼容（字段布局一致）。
- v1 的节点部分：标准库在拿不到 MAC 时用随机数代替，这是 `uuid` 模块的既有行为。
- v3/v5 的"确定性"指同一命名空间+名字永远得到同一 UUID；换名字就换值。
- UUID 不保证全局唯一，只保证冲突概率可忽略（v4/v7）；需要密码学唯一性请用 `secrets`（见兄弟项目 `passgen`）。

## 已知局限

- `--namespace` 只支持 `dns/url/oid/x500` 四个标准命名空间，不支持自定义 UUID 命名空间（有需要请提 issue）。
- v7 的时间戳精度是毫秒；同一毫秒内生成多个靠 74 位随机区分，不保证毫秒内有序。
