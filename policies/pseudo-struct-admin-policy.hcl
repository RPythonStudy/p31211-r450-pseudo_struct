# pseudo-struct 프로젝트 하위 모든 secret에
# 생성, 조회, 수정, 삭제, 목록 권한을 모두 허용하는 정책

path "secret/data/pseudo-struct/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
