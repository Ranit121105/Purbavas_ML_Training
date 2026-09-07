# Multi-Hazard Environmental Sensor Telemetry Dataset Generator (High-Fidelity)
$ErrorActionPreference = 'Stop'

$dataDirRaw = Join-Path $PSScriptRoot "..\..\data\raw"
$dataDirProcessed = Join-Path $PSScriptRoot "..\..\data\processed"

if (!(Test-Path $dataDirRaw)) { New-Item -ItemType Directory -Force -Path $dataDirRaw | Out-Null }
if (!(Test-Path $dataDirProcessed)) { New-Item -ItemType Directory -Force -Path $dataDirProcessed | Out-Null }

$nodes = @(
    @{ node_id='NODE_ASSAM_01'; region='Assam_Brahmaputra_Basin'; lat=26.1850; lon=91.7450; elevation=55.0; hazards=@('FLASH_FLOOD'); base_temp=28.0; base_hum=82.0; base_soil=55.0; base_water=3.2 },
    @{ node_id='NODE_BIHAR_02'; region='Bihar_Kosi_Basin'; lat=25.5941; lon=85.1376; elevation=53.0; hazards=@('FLASH_FLOOD'); base_temp=30.0; base_hum=78.0; base_soil=50.0; base_water=2.8 },
    @{ node_id='NODE_UK_FOREST_03'; region='Uttarakhand_Garhwal_Forest'; lat=30.3165; lon=78.0322; elevation=1450.0; hazards=@('FOREST_FIRE','LANDSLIDE_PRECURSOR'); base_temp=24.0; base_hum=45.0; base_soil=35.0; base_water=0.8 },
    @{ node_id='NODE_HP_HILLS_04'; region='Himachal_Pradesh_Hills'; lat=31.1048; lon=77.1734; elevation=2100.0; hazards=@('LANDSLIDE_PRECURSOR','FOREST_FIRE'); base_temp=19.0; base_hum=50.0; base_soil=40.0; base_water=0.6 },
    @{ node_id='NODE_DELHI_NCR_05'; region='Delhi_NCR_Urban'; lat=28.6139; lon=77.2090; elevation=216.0; hazards=@('HAZARDOUS_SMOG'); base_temp=32.0; base_hum=58.0; base_soil=25.0; base_water=1.2 },
    @{ node_id='NODE_WG_WAYANAD_06'; region='Western_Ghats_Wayanad'; lat=11.6854; lon=76.1320; elevation=820.0; hazards=@('LANDSLIDE_PRECURSOR','FLASH_FLOOD'); base_temp=23.0; base_hum=88.0; base_soil=60.0; base_water=1.5 },
    @{ node_id='NODE_GUJ_IND_07'; region='Gujarat_Industrial_Corridor'; lat=21.6032; lon=72.9774; elevation=25.0; hazards=@('INDUSTRIAL_CHEMICAL_LEAK','WATER_QUALITY_CRISIS'); base_temp=34.0; base_hum=65.0; base_soil=30.0; base_water=1.1 }
)

$headers = 'timestamp,node_id,region,latitude,longitude,elevation_m,water_level_m,water_level_rate_m_hr,rainfall_1h_mm,rainfall_6h_mm,rainfall_24h_mm,temperature_c,humidity_pct,heat_index_c,smoke_ppm,co_ppm,voc_ppb,so2_ug_m3,no2_ug_m3,pm25,pm10,aqi_calculated,soil_moisture_pct,vibration_g,tilt_angle_deg,water_ph,water_turbidity_ntu,dissolved_oxygen_mg_l,battery_voltage_v,signal_rssi_dbm,hazard_type,severity_level,flood_risk_score,fire_risk_score,air_pollution_risk_score,landslide_risk_score,chemical_hazard_risk_score'

$rand = New-Object System.Random(42)
$startTime = [datetime]::Parse('2026-06-01T00:00:00Z').ToUniversalTime()
$numDays = 90
$intervalMins = 30
$totalSteps = [int](($numDays * 24 * 60) / $intervalMins)

$nodeStates = @{}
foreach ($n in $nodes) {
    $nodeStates[$n.node_id] = @{
        water = [double]$n.base_water
        soil = [double]$n.base_soil
        tilt = [double](0.2 + $rand.NextDouble() * 0.2)
        event = 'NORMAL'
        event_steps = 0
        normal_steps = $rand.Next(30, 80)
        rain_hist = [System.Collections.ArrayList]@(0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0)
    }
}

$rows = New-Object System.Collections.Generic.List[string]

for ($step = 0; $step -lt $totalSteps; $step++) {
    $currDt = $startTime.AddMinutes($step * $intervalMins)
    $hour = $currDt.Hour
    $diurnalTemp = [Math]::Sin([Math]::PI * ($hour - 9) / 12.0) * 5.0
    $diurnalHum = -[Math]::Sin([Math]::PI * ($hour - 9) / 12.0) * 12.0

    foreach ($n in $nodes) {
        $nid = $n.node_id
        $st = $nodeStates[$nid]

        if ($st.event_steps -gt 0) {
            $st.event_steps = $st.event_steps - 1
            if ($st.event_steps -eq 0) {
                $st.event = 'NORMAL'
                $st.normal_steps = $rand.Next(40, 100)
            }
        } else {
            $st.normal_steps = $st.normal_steps - 1
            if ($st.normal_steps -le 0) {
                $possible = $n.hazards
                $st.event = $possible[$rand.Next(0, $possible.Count)]
                $st.event_steps = $rand.Next(16, 40)
            }
        }

        $event = $st.event
        $temp = [Math]::Max(10.0, $n.base_temp + $diurnalTemp + ($rand.NextDouble() * 2.0 - 1.0))
        $hum = [Math]::Min(100.0, [Math]::Max(15.0, $n.base_hum + $diurnalHum + ($rand.NextDouble() * 4.0 - 2.0)))
        $heatIdx = $temp + 0.05 * $hum

        $rain1h = 0.0
        if ($n.base_hum -gt 60.0 -and $rand.NextDouble() -lt 0.25) {
            $rain1h = [Math]::Round($rand.NextDouble() * 3.5, 2)
        }
        $smoke = [Math]::Max(5.0, 25.0 + ($rand.NextDouble() * 10.0 - 5.0))
        $co = [Math]::Max(0.1, 1.2 + ($rand.NextDouble() * 0.6 - 0.3))
        $voc = [Math]::Max(30.0, 120.0 + ($rand.NextDouble() * 40.0 - 20.0))
        $so2 = [Math]::Max(2.0, 12.0 + ($rand.NextDouble() * 6.0 - 3.0))
        $no2 = [Math]::Max(5.0, 22.0 + ($rand.NextDouble() * 8.0 - 4.0))
        $pm25 = [Math]::Max(10.0, 45.0 + ($rand.NextDouble() * 20.0 - 10.0))
        $pm10 = $pm25 * (1.5 + $rand.NextDouble() * 0.4)
        $vib = [Math]::Max(0.002, 0.008 + ($rand.NextDouble() * 0.004 - 0.002))
        $tilt = $st.tilt
        $ph = [Math]::Max(6.2, [Math]::Min(8.4, 7.3 + ($rand.NextDouble() * 0.4 - 0.2)))
        $turbidity = [Math]::Max(2.0, 12.0 + ($rand.NextDouble() * 6.0 - 3.0))
        $do2 = [Math]::Max(4.0, 7.5 + ($rand.NextDouble() * 0.8 - 0.4))
        $waterRate = 0.0

        $severity = 'NONE'
        $floodRisk = 0.05
        $fireRisk = 0.02
        $airRisk = 0.08
        $landslideRisk = 0.03
        $chemRisk = 0.01

        switch ($event) {
            'FLASH_FLOOD' {
                $rain1h = [Math]::Round(45.0 + $rand.NextDouble() * 60.0, 2)
                $st.water = [Math]::Min(12.0, $st.water + 0.50 + $rand.NextDouble() * 0.45)
                $waterRate = [Math]::Round(1.2 + $rand.NextDouble() * 1.4, 3)
                $st.soil = [Math]::Min(98.0, $st.soil + 6.0 + $rand.NextDouble() * 6.0)
                $turbidity = [Math]::Round(180.0 + $rand.NextDouble() * 350.0, 2)
                $do2 = [Math]::Max(2.5, $do2 - 2.0)
                $floodRisk = [Math]::Min(1.0, 0.65 + ($st.water / 12.0) * 0.35)
                $severity = if ($st.water -gt 6.5) { 'EMERGENCY_CRITICAL' } else { 'WARNING_HIGH' }
            }
            'FOREST_FIRE' {
                $temp = [Math]::Min(48.0, $temp + 12.0 + $rand.NextDouble() * 6.0)
                $hum = [Math]::Max(12.0, $hum - 25.0)
                $smoke = [Math]::Round(280.0 + $rand.NextDouble() * 550.0, 2)
                $co = [Math]::Round(22.0 + $rand.NextDouble() * 45.0, 2)
                $pm25 = [Math]::Round(320.0 + $rand.NextDouble() * 400.0, 2)
                $pm10 = $pm25 * (1.8 + $rand.NextDouble() * 0.5)
                $fireRisk = [Math]::Min(1.0, 0.70 + ($smoke / 800.0) * 0.3)
                $airRisk = [Math]::Min(1.0, 0.60 + ($pm25 / 750.0) * 0.4)
                $severity = if ($smoke -gt 450.0) { 'EMERGENCY_CRITICAL' } else { 'WARNING_HIGH' }
            }
            'HAZARDOUS_SMOG' {
                $pm25 = [Math]::Round(240.0 + $rand.NextDouble() * 320.0, 2)
                $pm10 = [Math]::Round(410.0 + $rand.NextDouble() * 450.0, 2)
                $so2 = [Math]::Round(55.0 + $rand.NextDouble() * 75.0, 2)
                $no2 = [Math]::Round(85.0 + $rand.NextDouble() * 95.0, 2)
                $co = [Math]::Round(6.5 + $rand.NextDouble() * 8.0, 2)
                $airRisk = [Math]::Min(1.0, 0.65 + ($pm25 / 550.0) * 0.35)
                $severity = if ($pm25 -gt 320.0) { 'EMERGENCY_CRITICAL' } else { 'WARNING_HIGH' }
            }
            'LANDSLIDE_PRECURSOR' {
                $rain1h = [Math]::Round(30.0 + $rand.NextDouble() * 45.0, 2)
                $st.soil = [Math]::Min(99.0, [Math]::Max(84.0, $st.soil + 4.0 + $rand.NextDouble() * 3.0))
                $vib = [Math]::Round(0.14 + $rand.NextDouble() * 0.35, 4)
                $st.tilt = [Math]::Min(20.0, $st.tilt + 0.8 + $rand.NextDouble() * 1.5)
                $tilt = $st.tilt
                $turbidity = [Math]::Round(160.0 + $rand.NextDouble() * 220.0, 2)
                $landslideRisk = [Math]::Min(1.0, ($st.soil / 100.0) * 0.5 + ($vib / 0.4) * 0.5)
                $severity = if ($vib -gt 0.22 -or $tilt -gt 5.0) { 'EMERGENCY_CRITICAL' } else { 'WARNING_HIGH' }
            }
            'INDUSTRIAL_CHEMICAL_LEAK' {
                $voc = [Math]::Round(2200.0 + $rand.NextDouble() * 5500.0, 2)
                $so2 = [Math]::Round(110.0 + $rand.NextDouble() * 180.0, 2)
                $no2 = [Math]::Round(120.0 + $rand.NextDouble() * 150.0, 2)
                $co = [Math]::Round(16.0 + $rand.NextDouble() * 28.0, 2)
                $chemRisk = [Math]::Min(1.0, 0.70 + ($voc / 7500.0) * 0.3)
                $severity = if ($voc -gt 3800.0) { 'EMERGENCY_CRITICAL' } else { 'WARNING_HIGH' }
            }
            'WATER_QUALITY_CRISIS' {
                $ph = if ($rand.NextDouble() -lt 0.5) { [Math]::Round(4.0 + $rand.NextDouble() * 1.2, 2) } else { [Math]::Round(9.8 + $rand.NextDouble() * 1.5, 2) }
                $turbidity = [Math]::Round(180.0 + $rand.NextDouble() * 300.0, 2)
                $do2 = [Math]::Max(1.0, [Math]::Round(1.5 + $rand.NextDouble() * 1.5, 2))
                $chemRisk = [Math]::Min(1.0, 0.60 + ($turbidity / 500.0) * 0.4)
                $severity = 'WARNING_HIGH'
            }
            Default {
                # Smooth, rapid return to baseline during normal periods
                $st.water = [Math]::Max([double]$n.base_water, $st.water - 0.40)
                $st.soil = [Math]::Max([double]$n.base_soil, $st.soil - 0.8)
                $st.tilt = [Math]::Max(0.2, $st.tilt - 0.3)
                $tilt = $st.tilt
            }
        }

        $st.rain_hist.RemoveAt(0)
        [void]$st.rain_hist.Add($rain1h)
        $rain6h = 0.0
        foreach ($r in $st.rain_hist) { $rain6h += $r }
        $rain6h = [Math]::Round($rain6h, 2)
        $rain24h = [Math]::Round($rain6h * (2.0 + $rand.NextDouble()), 2)

        $aqi = 50.0
        if ($pm25 -le 30) { $aqi = $pm25 * (50.0/30.0) }
        elseif ($pm25 -le 60) { $aqi = 50.0 + ($pm25 - 30.0) * (50.0/30.0) }
        elseif ($pm25 -le 90) { $aqi = 100.0 + ($pm25 - 60.0) * (100.0/30.0) }
        elseif ($pm25 -le 120) { $aqi = 200.0 + ($pm25 - 90.0) * (100.0/30.0) }
        elseif ($pm25 -le 250) { $aqi = 300.0 + ($pm25 - 120.0) * (100.0/130.0) }
        else { $aqi = 400.0 + ($pm25 - 250.0) * (100.0/130.0) }
        $aqi = [Math]::Min(500.0, [Math]::Max(15.0, [Math]::Round($aqi, 1)))

        $batt = [Math]::Round(3.7 + $rand.NextDouble() * 0.45, 2)
        $rssi = [Math]::Round(-105.0 + $rand.NextDouble() * 35.0, 1)

        $line = [string]::Format([System.Globalization.CultureInfo]::InvariantCulture,
            '{0},{1},{2},{3:F4},{4:F4},{5:F1},{6:F2},{7:F3},{8:F2},{9:F2},{10:F2},{11:F2},{12:F2},{13:F2},{14:F2},{15:F2},{16:F2},{17:F2},{18:F2},{19:F2},{20:F2},{21:F1},{22:F2},{23:F4},{24:F2},{25:F2},{26:F2},{27:F2},{28:F2},{29:F1},{30},{31},{32:F3},{33:F3},{34:F3},{35:F3},{36:F3}',
            $currDt.ToString('yyyy-MM-ddTHH:mm:ssZ'),
            $nid, $n.region, $n.lat, $n.lon, $n.elevation,
            $st.water, $waterRate, $rain1h, $rain6h, $rain24h,
            $temp, $hum, $heatIdx,
            $smoke, $co, $voc, $so2, $no2,
            $pm25, $pm10, $aqi,
            $st.soil, $vib, $tilt,
            $ph, $turbidity, $do2,
            $batt, $rssi,
            $event, $severity,
            $floodRisk, $fireRisk, $airRisk, $landslideRisk, $chemRisk
        )
        $rows.Add($line)
    }
}

$rawPath = Join-Path $dataDirRaw 'environmental_sensor_telemetry.csv'
$trainPath = Join-Path $dataDirProcessed 'train_data.csv'
$testPath = Join-Path $dataDirProcessed 'test_data.csv'

[System.IO.File]::WriteAllLines($rawPath, @($headers) + $rows)
$splitIdx = [int]($rows.Count * 0.8)

$trainRows = $rows.GetRange(0, $splitIdx)
$testRows = $rows.GetRange($splitIdx, $rows.Count - $splitIdx)

[System.IO.File]::WriteAllLines($trainPath, @($headers) + $trainRows)
[System.IO.File]::WriteAllLines($testPath, @($headers) + $testRows)

Write-Host ('[SUCCESS] Generated total records: ' + $rows.Count)
Write-Host ('Saved Raw: ' + $rawPath + ' (' + (Get-Item $rawPath).Length + ' bytes)')
Write-Host ('Saved Train Split: ' + $trainPath + ' (' + $trainRows.Count + ' rows)')
Write-Host ('Saved Test Split: ' + $testPath + ' (' + $testRows.Count + ' rows)')
