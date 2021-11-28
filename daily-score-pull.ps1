if(-not (Test-Path "$PSScriptRoot/players.json")){
    throw "Could not find players.json file!"
}

. "$PSScriptRoot/highscores-functions.ps1"

$players = Get-Content "$PSScriptRoot/players.json" | ConvertFrom-Json

$players | %{
    "Pulling scores for player: $_"
    $scores = GetPlayerStats $_
    
    if(Test-Path -Path "$PSScriptRoot/data/$_.json" -PathType Leaf)
    {
        "Found existing $PSScriptRoot/data/$_.json file. Appending new scores."
        $currentScores = Get-Content "$PSScriptRoot/data/$_.json" | ConvertFrom-Json
        $currentScores = @($currentScores) + @($scores)
    }
    else
    {
        "Could not find $PSScriptRoot/data/$_.json file. A new one will be created."
        $currentScores = $scores
    }

    $currentScores | ConvertTo-Json -Depth 20 -Compress | Set-Content -Force "$PSScriptRoot/data/$_.json"
}