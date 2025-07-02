#!/usr/bin/env bash
set -euo pipefail

# --- 환경변수/경로 변수 선언 ---
VAULT_CONTAINER=vault
CERT_DIR=./docker/vault/certs

# 1. pki 엔진 mount 및 튠
sudo docker exec $VAULT_CONTAINER vault secrets enable pki || true
sudo docker exec $VAULT_CONTAINER vault secrets tune -max-lease-ttl=8760h pki

# 2. Root CA 발급
sudo docker exec $VAULT_CONTAINER vault write pki/root/generate/internal \
    common_name="KIRAMS RPythonStudy PseudoStruct CA" \
    ttl=8760h

# 3. CRL, issuing cert URL 설정
sudo docker exec $VAULT_CONTAINER vault write pki/config/urls \
    issuing_certificates="http://127.0.0.1:8200/v1/pki/ca" \
    crl_distribution_points="http://127.0.0.1:8200/v1/pki/crl"

# 4. Role 생성
sudo docker exec $VAULT_CONTAINER vault write pki/roles/example-dot-com \
    allowed_domains="localhost,elasticsearch,kibana,logstash,keycloak,vault,openldap" \
    allow_subdomains=true \
    allow_bare_domains=true \
    allow_ip_sans=true \
    allow_localhost=true \
    max_ttl="168h"

# 5. 인증서 발급
sudo docker exec $VAULT_CONTAINER vault write -format=json pki/issue/example-dot-com \
    common_name=localhost \
    alt_names="localhost,elasticsearch,kibana,logstash,keycloak,vault,openldap" \
    ip_sans=127.0.0.1 \
    ttl=168h \
    > cert.json 2>/dev/null

# 6. 인증서, 프라이빗키, CA, 체인 추출
jq -r '.data.certificate' cert.json > vault.crt
jq -r '.data.private_key' cert.json > vault.key
jq -r '.data.issuing_ca' cert.json > ca.crt
jq -r '.data.ca_chain[]?' cert.json > chain.crt

# 7. 마운트 폴더로 복사
sudo cp vault.crt vault.key $CERT_DIR/

# 8. 권한 설정
sudo chown 100:100 $CERT_DIR/vault.key

echo "Vault PKI 인증서 자동화 완료!"
