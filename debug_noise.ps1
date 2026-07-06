Add-Type @"
using System;
public class NoiseDebug {
    public const float RANGE = 45f;

    public static float ComputeNoise(float ax, float ay, float bx, float by, int i) {
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
}
"@

function Analyze-Edge($label, $ax, $ay, $bx, $by, $count = 10) {
    Write-Host ""
    Write-Host "=== $label ($ax,$ay) -> ($bx,$by) ===" -ForegroundColor Cyan
    $values = @()
    for ($i = 0; $i -lt $count; $i++) {
        $n = [NoiseDebug]::ComputeNoise($ax, $ay, $bx, $by, $i)
        $values += $n
        $sign = if ($n -ge 0) { "+" } else { "-" }
        $line = "  i={0:00}  noise={1,8:+0.00;-0.00}  sign={2}" -f $i, $n, $sign
        Write-Host $line
    }
    $seq = ($values | ForEach-Object { if ($_ -ge 0) { "+" } else { "-" } }) -join ""
    $pos = ($values | Where-Object { $_ -ge 0 }).Count
    $neg = $count - $pos
    $flips = 0
    for ($j = 1; $j -lt $count; $j++) {
        if (($values[$j-1] -ge 0) -ne ($values[$j] -ge 0)) { $flips++ }
    }
    Write-Host ("  signs: {0}  ({1}+ / {2}-)  flips={3}/{4}" -f $seq, $pos, $neg, $flips, ($count-1)) -ForegroundColor Yellow
}

Analyze-Edge "Edge A 수평" 0.0 0.0 300.0 0.0
Analyze-Edge "Edge B 대각선" -150.0 200.0 150.0 -50.0
Analyze-Edge "Edge C 수직" 100.0 -100.0 100.0 200.0
Analyze-Edge "Edge D 짧은 라인" 50.0 50.0 110.0 80.0
Analyze-Edge "Edge E 비대칭 좌표" -42.7 13.5 178.3 -91.2
Analyze-Edge "Edge F 격자형 좌표" 100.0 100.0 200.0 100.0
Analyze-Edge "Edge G 격자형 좌표" 200.0 100.0 300.0 100.0

# 100 edges 통계
Write-Host ""
Write-Host "=== 100 edges x 8 dots = 800 dots stats ===" -ForegroundColor Green
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
        $edgeVals += [NoiseDebug]::ComputeNoise($ax, $ay, $bx, $by, $i)
    }
    $totalPos += ($edgeVals | Where-Object { $_ -ge 0 }).Count
    for ($j = 1; $j -lt 8; $j++) {
        if (($edgeVals[$j-1] -ge 0) -ne ($edgeVals[$j] -ge 0)) { $totalFlips++ }
        $totalPairs++
    }
}
Write-Host ("  positive ratio: {0}/800 = {1:0.0}% (50% expected)" -f $totalPos, ($totalPos/8.0))
Write-Host ("  flip ratio: {0}/{1} = {2:0.0}% (50% expected if random)" -f $totalFlips, $totalPairs, ($totalFlips * 100.0 / $totalPairs))
