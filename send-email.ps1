param(
    [switch]$LocalTest
)

if($env:OS -eq 'Windows_NT' -and -not $env:VIRTUAL_ENV){
    "Creating virtual env..."
    python -m venv venv
    ./venv/Scripts/activate
}

python -m pip install -r requirements.txt

if($LocalTest){
    python analysis.py --files (Get-ChildItem data -File -Filter *.json | ForEach-Object{$_.FullName})
}else {
    if(-not $env:S3_BUCKET_URL){ throw 'Could not find requried env var S3_BUCKET_URL' }
    python analysis.py --bucket-url $env:S3_BUCKET_URL --files (Get-ChildItem data -File -Filter *.json | ForEach-Object{$_.FullName})
}

if(-not (Test-Path email_content.html)){
    throw 'Could not find email_content.html file. It should have been produced by analysis.py'
}
if(-not (Test-Path images_to_upload.json)){
    throw 'Could not find email_content.html file. It should have been produced by analysis.py'
}

if(-not $LocalTest){
    if(-not $env:S3_BUCKET_NAME){ throw 'Could not find requried env var S3_BUCKET_NAME' }

    aws s3 cp email_content.html s3://$env:S3_BUCKET_NAME/email_content.html

    (Get-Content images_to_upload.json | ConvertFrom-Json) | %{ 
        "Uploading $_ to s3!"  
        aws s3 cp "`"$_`"" "`"s3://$env:S3_BUCKET_NAME/$_`""
    }

    python send-emails.py --html-file 'email_content.html'
}
