#!/usr/bin/env python3
"""uuidgen - 终端 UUID 生成器，支持 v1/v3/v5/v7 四种版本。

纯标准库实现。v7（Python < 3.14 无 uuid.uuid7）按 RFC 9562 手工构造：
48 位 Unix 毫秒时间戳 + 4 位版本号 + 12 位随机 + 2 位 variant + 62 位随机。
"""

import argparse
import random
import sys
import time
import uuid

NAMESPACES = {
    "dns": uuid.NAMESPACE_DNS,
    "url": uuid.NAMESPACE_URL,
    "oid": uuid.NAMESPACE_OID,
    "x500": uuid.NAMESPACE_X500,
}


def make_v7() -> uuid.UUID:
    """手工构造 RFC 9562 v7 UUID（48 位毫秒时间戳 + 74 位随机）。"""
    unix_ms = int(time.time() * 1000)
    rand_a = random.getrandbits(12)
    rand_b = random.getrandbits(62)
    # 布局：48 位时间戳 | 4 位版本(0111) | 12 位随机 | 2 位 variant(10) | 62 位随机
    value = (unix_ms << 80) | (0b0111 << 76) | (rand_a << 64) | (0b10 << 62) | rand_b
    return uuid.UUID(int=value)


def generate(args) -> list[uuid.UUID]:
    if args.v1:
        maker = uuid.uuid1
    elif args.v3:
        maker = lambda: uuid.uuid3(_namespace(args), args.name or "")
    elif args.v5:
        maker = lambda: uuid.uuid5(_namespace(args), args.name or "")
    elif args.v7:
        maker = make_v7
    else:
        maker = uuid.uuid4
    return [maker() for _ in range(args.count)]


def _namespace(args) -> uuid.UUID:
    return NAMESPACES[args.namespace]


def format_uuid(u: uuid.UUID, args) -> str:
    s = u.hex if args.no_dashes else str(u)
    return s.upper() if args.upper else s


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="uuidgen",
        description="终端 UUID 生成器：默认 v4，支持 v1/v3/v5/v7。",
    )
    ver = p.add_mutually_exclusive_group()
    ver.add_argument("--v1", action="store_true", help="版本 1（时间 + MAC/随机节点）")
    ver.add_argument("--v3", action="store_true", help="版本 3（MD5 命名空间，确定性）")
    ver.add_argument("--v5", action="store_true", help="版本 5（SHA-1 命名空间，确定性）")
    ver.add_argument("--v7", action="store_true", help="版本 7（时间排序，RFC 9562）")
    p.add_argument("--namespace", choices=sorted(NAMESPACES), default="dns",
                   help="v3/v5 的命名空间（默认 dns）")
    p.add_argument("--name", default="", help="v3/v5 的名字输入")
    p.add_argument("--count", type=int, default=1, help="生成个数（默认 1）")
    p.add_argument("--no-dashes", action="store_true", help="去掉连字符（32 位 hex）")
    p.add_argument("--upper", action="store_true", help="大写输出")
    p.add_argument("--version", action="version", version="uuidgen 0.1.0")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.count < 1:
        print("error: --count 必须 >= 1", file=sys.stderr)
        return 2
    if (args.v3 or args.v5) and not args.name:
        print("error: --v3/--v5 需要 --name 指定名字输入", file=sys.stderr)
        return 2
    for u in generate(args):
        print(format_uuid(u, args))
    return 0


if __name__ == "__main__":
    sys.exit(main())
