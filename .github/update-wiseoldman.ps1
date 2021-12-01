$players = get-content 'players.json' | ConvertFrom-Json

$players | %{
    Invoke-WebRequest -Uri 'https://api.wiseoldman.net/players/track/' -Method POST -Body @{username= $_}
}