if(-not (Test-Path "players.json")){
    throw "Could not find players.json file!"
}

. "./highscores-functions.ps1"

$timestamp = GetUnixTime

$players = Get-Content "players.json" | ConvertFrom-Json

$players | %{
    "Pulling scores for player: $_"
    $scores = GetPlayerStats $_ $timestamp
    
    if(Test-Path -Path "data/$_.json" -PathType Leaf)
    {
        "Found existing data/$_.json file. Appending new scores."
        $currentScores = Get-Content "data/$_.json" | ConvertFrom-Json
        $currentScores = @($currentScores) + @($scores)
    }
    else
    {
        "Could not find data/$_.json file. A new one will be created."
        $currentScores = $scores
    }

    $currentScores | ConvertTo-Json -Depth 20 -Compress | Set-Content -Force "data/$_.json"
}