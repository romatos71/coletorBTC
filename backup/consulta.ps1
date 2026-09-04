while ($true) {
    $ts = oc exec deployment/valkey-db -- valkey-cli get bitcoin:ultima_atualizacao
    $usd = oc exec deployment/valkey-db -- valkey-cli get bitcoin:preco_usd
    $brl = oc exec deployment/valkey-db -- valkey-cli get bitcoin:preco_brl
    
    Write-Output "$ts Em USD $usd Em Reais $brl"
    
    Start-Sleep -Seconds 15
}