$stagedBackend = (Resolve-Path -LiteralPath "$PSScriptRoot/backend").Path
$existingBackend = (Resolve-Path -LiteralPath "$PSScriptRoot/../../immobilier-backend-main/immobilier-backend-main").Path
$backendBackup = (Resolve-Path -LiteralPath "$PSScriptRoot/backup").Path
$backendFiles = @((Get-Item -LiteralPath "$stagedBackend/pom.xml")) + @(Get-ChildItem -LiteralPath "$stagedBackend/src" -Recurse -File)
foreach ($backendFile in $backendFiles) {
    $relativeFile = $backendFile.FullName.Substring($stagedBackend.Length + 1)
    $destinationFile = Join-Path $existingBackend $relativeFile
    $backupFile = Join-Path $backendBackup $relativeFile
    if ((Test-Path -LiteralPath $backupFile) -and (Test-Path -LiteralPath $destinationFile)) {
        if ((Get-FileHash -LiteralPath $backupFile).Hash -ne (Get-FileHash -LiteralPath $destinationFile).Hash) {
            throw "Le fichier $relativeFile a été modifié depuis la sauvegarde. Copie arrêtée."
        }
    }
}
foreach ($backendFile in $backendFiles) {
    $relativeFile = $backendFile.FullName.Substring($stagedBackend.Length + 1)
    $destinationFile = Join-Path $existingBackend $relativeFile
    New-Item -ItemType Directory -Force -Path (Split-Path $destinationFile -Parent) | Out-Null
    Copy-Item -LiteralPath $backendFile.FullName -Destination $destinationFile -Force
}
Write-Output "Intégration appliquée à $existingBackend ; sauvegarde dans $backendBackup."
