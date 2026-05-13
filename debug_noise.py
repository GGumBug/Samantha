"""
UIDottedLine.ComputeRotationNoiseDeg 의 현재 알고리즘 (xorshift32) 재현 + 분포 측정.
실제 코드와 동일한 hash 계산 + xorshift32 finalize 적용.
"""
import struct

MASK32 = 0xFFFFFFFF
ROTATION_NOISE_RANGE_DEG = 45.0


def float_hash(f):
    """float.GetHashCode() 재현 — .NET 의 단순 비트 재해석"""
    bits = struct.unpack('i', struct.pack('f', f))[0]
    return bits


def compute_noise(ax, ay, bx, by, i, range_deg=ROTATION_NOISE_RANGE_DEG):
    """현재 UIDottedLine.cs 의 ComputeRotationNoiseDeg 알고리즘 재현"""
    # int 연산 (overflow wrap)
    h = 23
    h = ((h * 37) + float_hash(ax)) & MASK32
    h = ((h * 37) + float_hash(ay)) & MASK32
    h = ((h * 37) + float_hash(bx)) & MASK32
    h = ((h * 37) + float_hash(by)) & MASK32
    h = ((h * 37) + i) & MASK32

    # xorshift32 (Marsaglia)
    x = h & MASK32
    x ^= (x << 13) & MASK32
    x ^= x >> 17
    x ^= (x << 5) & MASK32

    norm = x / float(MASK32)
    return (norm * 2.0 - 1.0) * range_deg


def analyze_edge(label, ax, ay, bx, by, dot_count=10):
    """한 edge 의 dot_count 개 noise 값 출력 + 부호 시퀀스 분석"""
    print(f"\n=== {label}: ({ax},{ay}) → ({bx},{by}) ===")
    values = []
    for i in range(dot_count):
        n = compute_noise(ax, ay, bx, by, i)
        values.append(n)
        sign = '+' if n >= 0 else '-'
        print(f"  i={i:2d}: noise={n:+7.2f}  sign={sign}")

    # 부호 시퀀스
    seq = ''.join('+' if v >= 0 else '-' for v in values)
    pos = sum(1 for v in values if v >= 0)
    neg = dot_count - pos
    print(f"  signs: {seq}  ({pos}+ / {neg}-)")

    # 인접 부호 교차 횟수
    flips = sum(1 for j in range(1, dot_count) if (values[j-1] >= 0) != (values[j] >= 0))
    print(f"  flips: {flips}/{dot_count-1}  (50% expected if random: {(dot_count-1)/2:.1f})")


# 가상 edge 들 — 다양한 좌표 입력으로 분포 확인
analyze_edge("Edge A — 수평", 0.0, 0.0, 300.0, 0.0)
analyze_edge("Edge B — 대각선", -150.0, 200.0, 150.0, -50.0)
analyze_edge("Edge C — 수직", 100.0, -100.0, 100.0, 200.0)
analyze_edge("Edge D — 짧은 라인", 50.0, 50.0, 110.0, 80.0)
analyze_edge("Edge E — 비대칭 좌표", -42.7, 13.5, 178.3, -91.2)

# 전체 통계 (100 edges, 8 dots each)
print("\n=== 전체 통계 (100 edges × 8 dots = 800 dots) ===")
import random
random.seed(42)
total_pos = 0
total_flips = 0
total_pairs = 0
for _ in range(100):
    ax = random.uniform(-500, 500)
    ay = random.uniform(-500, 500)
    bx = random.uniform(-500, 500)
    by = random.uniform(-500, 500)
    edge_values = [compute_noise(ax, ay, bx, by, i) for i in range(8)]
    total_pos += sum(1 for v in edge_values if v >= 0)
    total_flips += sum(1 for j in range(1, 8) if (edge_values[j-1] >= 0) != (edge_values[j] >= 0))
    total_pairs += 7

print(f"  전체 양수 비율: {total_pos}/800 = {total_pos/800*100:.1f}% (50% 기대)")
print(f"  인접 부호 교차율: {total_flips}/{total_pairs} = {total_flips/total_pairs*100:.1f}% (50% 기대 if random)")
