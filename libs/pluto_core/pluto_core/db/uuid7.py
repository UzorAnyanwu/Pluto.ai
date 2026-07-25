"""RFC 9562 UUIDv7 generation.

Every tenant-owned primary key uses UUIDv7 instead of an auto-increment integer or UUIDv4 — see
docs/architecture/01-system-architecture.md Decision 4. UUIDv7 is time-ordered, which keeps B-tree
index insert patterns sequential (avoiding the random-insert index bloat plain UUIDv4 causes at
high write volume) while still being a UUID (no cross-tenant row-count leakage, portable across a
future database-per-shard split).

Implemented directly rather than pulling in a third-party package: the algorithm is small,
stable (fixed by RFC 9562), and this avoids a dependency on a package whose maintenance status
isn't guaranteed.
"""

import os
import time
import uuid


def uuid7() -> uuid.UUID:
    """Generate a UUIDv7: 48-bit millisecond Unix timestamp + version/variant bits + random tail."""
    unix_ts_ms = int(time.time() * 1000)
    ts_bytes = unix_ts_ms.to_bytes(6, byteorder="big")
    rand_bytes = bytearray(os.urandom(10))

    # Byte 6: top 4 bits = version (0111 = 7), bottom 4 bits = random.
    rand_bytes[0] = (rand_bytes[0] & 0x0F) | 0x70
    # Byte 8: top 2 bits = variant (10), bottom 6 bits = random.
    rand_bytes[2] = (rand_bytes[2] & 0x3F) | 0x80

    return uuid.UUID(bytes=bytes(ts_bytes) + bytes(rand_bytes))
