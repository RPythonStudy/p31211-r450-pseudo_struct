# pseudo-struct 프로젝트 하위 secret(예: ff3 암호화키)에 대해
# 조회(read)와 목록(list)만 허용하는 최소권한 정책

path "secret/data/pseudo-struct/*" {
  capabilities = ["read", "list"]
}
