# The score stat parsing code is based on https://github.com/Judaxx/osrs-json-api

$STATS = @{
    skills= @('overall','attack','defence','strength','hitpoints','ranged','prayer','magic','cooking','woodcutting','fletching','fishing','firemaking','crafting','smithing','mining','herblore','agility','thieving','slayer','farming','runecraft','hunter','construction');
    bh= @('hunter', 'rogue');
    clues= @('all', 'beginner', 'easy', 'medium', 'hard', 'elite', 'master');
    bosses= @('Abyssal Sire','Alchemical Hydra','Barrows Chests','Bryophyta','Callisto','Cerberus','Chambers of Xeric','Chambers of Xeric: Challenge Mode','Chaos Elemental','Chaos Fanatic','Commander Zilyana','Corporeal Beast','Crazy Archaeologist','Dagannoth Prime','Dagannoth Rex','Dagannoth Supreme','Deranged Archaeologist','General Graardor','Giant Mole','Grotesque Guardians','Hespori','Kalphite Queen','King Black Dragon','Kraken',"Kree'Arra","K'ril Tsutsaroth",'Mimic','Nightmare',"Phosani's Nightmare",'Obor','Sarachnis','Scorpia','Skotizo','Tempoross','The Gauntlet','The Corrupted Gauntlet','Theatre of Blood','Theatre of Blood: Hard Mode','Thermonuclear Smoke Devil','TzKal-Zuk','TzTok-Jad','Venenatis',"Vet'ion",'Vorkath','Wintertodt','Zalcano','Zulrah')
}

function GetScores([string]$PlayerName){
    return (Invoke-WebRequest "http://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player=$PlayerName").Content
}

function parseSkills($statsArray) {
    $playerStats = $statsArray[0..23]
    $skills = @{}

    for ($i=0; $i -lt $STATS.skills.count; $i++){
        $skills[$STATS.skills[$i]] = @{ rank = $playerStats[$i][0]; level = $playerStats[$i][1]; xp = $playerStats[$i][2]}
    }
    return $skills;
}

function parseBH($statsArray){
    $playerStats = $statsArray[24..25]
    $bh = @{}

    for ($i=0; $i -lt $STATS.bh.count; $i++){
        if($playerStats[$i][1] -eq -1){ continue }
        $bh[$STATS.bh[$i]] = @{ rank = $playerStats[$i][0]; score = $playerStats[$i][1] }
    }
    if($bh.Keys.Count -eq 0){ return $null}
    return $bh;
}

function parseLMS($statsArray){
    if($statsArray[26][1] -eq -1){ return $null}
    return @{ rank = $statsArray[26][0]; score = $statsArray[26][1] }
}

function parseClues($statsArray){
    $playerStats = $statsArray[27..33]
    $clues = @{}

    for ($i=0; $i -lt $STATS.clues.count; $i++){
        if($playerStats[$i][1] -eq -1){ continue }
        $clues[$STATS.clues[$i]] = @{ rank = $playerStats[$i][0]; score = $playerStats[$i][1] }
    }

    return $clues
}

function parseSoulWarsZeal($statsArray){
    if($statsArray[35][1] -eq -1){ return $null }
    return @{ rank = $statsArray[35][0]; score = $statsArray[35][1] }
}

function parseBosses($statsArray){
    $playerStats = $statsArray[36..82]
    $bosses = @{}

    for ($i=0; $i -lt $STATS.bosses.count; $i++){
        if($playerStats[$i][1] -eq -1){ continue }
        $bosses[$STATS.bosses[$i]] = @{ rank = $playerStats[$i][0]; score = $playerStats[$i][1] }
    }
    return $bosses
}
 
function parseStats($statsArray){
    if(-not $statsArray -or -not ($statsArray -is [array]) -or $statsArray.Count -ne 84){
        throw "Stats array is invalid! Something's gone very wrong here."
    }

    return @{
        skills = parseSkills $statsArray
        bh = parseBH $statsArray
        lms = parseLMS $statsArray
        clues = parseClues $statsArray
        soulWarsZel = parseSoulWarsZeal $statsArray
        bosses = parseBosses $statsArray
    };
};

function GetUnixTime(){
    return [int64](([datetime]::UtcNow)-(get-date "1/1/1970")).TotalSeconds
}

function GetPlayerStats([string]$PlayerName, $Timestamp){
    $scoresArray = (GetScores $PlayerName) -split "`n" | %{, $_.Trim().Split(",")}
    $stats = (parseStats $scoresArray)
    $stats.timestamp = $Timestamp
    $stats
}

function Convert-FromUnixDate($UnixDate) {
    [timezone]::CurrentTimeZone.ToLocalTim22e(([datetime]'1/1/1970').AddSeconds($UnixDate))
}
