Add-Type @"
using System;
public class NoiseDebug {
    public const float RANGE = 45f;

    // 후보 1: 현재 xorshift32 (재측정)
    public static float Xorshift32(float ax, float ay, float bx, float by, int i) {
        unchecked {
            int h = 23;
            h = h * 37 + ax.GetHashCode();
            h = h * 37 + ay.GetHashCode();
            h = h * 37 + bx.GetHashCode();
            h = h * 37 + by.GetHashCode();
            h = h * 37 + i;
            uint x = (uint)h;
            x ^= x << 13;
            x ^= x >> 17;
            x ^= x << 5;
            float norm = x / (float)uint.MaxValue;
            return (norm * 2f - 1f) * RANGE;
        }
    }

    // 후보 2: Murmur3 32-bit finalizer
    public static float Murmur3(float ax, float ay, float bx, float by, int i) {
        unchecked {
            int h = 23;
            h = h * 37 + ax.GetHashCode();
            h = h * 37 + ay.GetHashCode();
            h = h * 37 + bx.GetHashCode();
            h = h * 37 + by.GetHashCode();
            h = h * 37 + i;
            uint x = (uint)h;
            x ^= x >> 16;
            x *= 0x85ebca6bu;
            x ^= x >> 13;
            x *= 0xc2b2ae35u;
            x ^= x >> 16;
            float norm = x / (float)uint.MaxValue;
            return (norm * 2f - 1f) * RANGE;
        }
    }

    // 후보 3: SplitMix32
    public static float SplitMix32(float ax, float ay, float bx, float by, int i) {
        unchecked {
            int h = 23;
            h = h * 37 + ax.GetHashCode();
            h = h * 37 + ay.GetHashCode();
            h = h * 37 + bx.GetHashCode();
            h = h * 37 + by.GetHashCode();
            h = h * 37 + i;
            uint x = (uint)h;
            x = (x ^ (x >> 16)) * 0x21f0aaadu;
            x = (x ^ (x >> 15)) * 0x735a2d97u;
            x = x ^ (x >> 15);
            float norm = x / (float)uint.MaxValue;
            return (norm * 2f - 1f) * RANGE;
        }
    }
}
"@

function Test-Algorithm($name, $func) {
    Write-Host ""
    Write-Host "########## $name ##########" -ForegroundColor Magenta

    # 5개 대표 edge 각각 10 dots
    $edges = @(
        @{ Label = "A 수평"; Ax = 0.0; Ay = 0.0; Bx = 300.0; By = 0.0 }
        @{ Label = "B 대각선"; Ax = -150.0; Ay = 200.0; Bx = 150.0; By = -50.0 }
        @{ Label = "C 수직"; Ax = 100.0; Ay = -100.0; Bx = 100.0; By = 200.0 }
        @{ Label = "F 격자"; Ax = 100.0; Ay = 100.0; Bx = 200.0; By = 100.0 }
        @{ Label = "G 격자"; Ax = 200.0; Ay = 100.0; Bx = 300.0; By = 100.0 }
    )

    foreach ($e in $edges) {
        $vals = @()
        $signs = ""
        for ($i = 0; $i -lt 10; $i++) {
            $n = & $func $e.Ax $e.Ay $e.Bx $e.By $i
            $vals += $n
            $signs += if ($n -ge 0) { "+" } else { "-" }
        }
        $flips = 0
        for ($j = 1; $j -lt 10; $j++) {
            if (($vals[$j-1] -ge 0) -ne ($vals[$j] -ge 0)) { $flips++ }
        }
        $minV = ($vals | Measure-Object -Minimum).Minimum
        $maxV = ($vals | Measure-Object -Maximum).Maximum
        $range = $maxV - $minV
        Write-Host ("  {0,-12} signs={1}  range=[{2,7:+0.0;-0.0} ~ {3,7:+0.0;-0.0}] span={4,5:0.0}  flip={5}/9" -f $e.Label, $signs, $minV, $maxV, $range, $flips)
    }

    # 100 edges 통계
    $rng = New-Object Random 42
    $totalPos = 0
    $totalFlips = 0
    $totalPairs = 0
    for ($e = 0; $e -lt 100; $e++) {
        $ax = ($rng.NextDouble() * 1000.0) - 500.0
        $ay = ($rng.NextDouble() * 1000.0) - 500.0
        $bx = ($rng.NextDouble() * 1000.0) - 500.0
        $by = ($rng.NextDouble() * 1000.0) - 500.0
        $edgeVals = @()
        for ($i = 0; $i -lt 8; $i++) {
            $edgeVals += & $func $ax $ay $bx $by $i
        }
        $totalPos += ($edgeVals | Where-Object { $_ -ge 0 }).Count
        for ($j = 1; $j -lt 8; $j++) {
            if (($edgeVals[$j-1] -ge 0) -ne ($edgeVals[$j] -ge 0)) { $totalFlips++ }
            $totalPairs++
        }
    }
    Write-Host ("  100 edges stats: positive={0}/800 ({1:0}%)  flip_rate={2:0.0}% (50% if random)" -f $totalPos, ($totalPos/8.0), ($totalFlips * 100.0 / $totalPairs)) -ForegroundColor Yellow
}

Test-Algorithm "Xorshift32 (현재)" { param($ax,$ay,$bx,$by,$i) [NoiseDebug]::Xorshift32($ax,$ay,$bx,$by,$i) }
Test-Algorithm "Murmur3 finalizer" { param($ax,$ay,$bx,$by,$i) [NoiseDebug]::Murmur3($ax,$ay,$bx,$by,$i) }
Test-Algorithm "SplitMix32" { param($ax,$ay,$bx,$by,$i) [NoiseDebug]::SplitMix32($ax,$ay,$bx,$by,$i) }
