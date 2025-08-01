# Pseudonymized Health Data Structuring Platform

## 개요

이 프로젝트는 의료 데이터(예: EMR, 병리보고서, 영상판독보고서 등)를 **개인정보보호에 적합하도록 가명화**하고, **비정형 데이터는 정형화**하여 임상 연구 및 AI 학습 데이터로 활용할 수 있도록 지원하는 오픈소스 플랫폼을 개발하고자 합니다.

-   **가명화:** 개인정보보호에 적합하면서도 임상연구에 적합한 가명화
-   **정형화:** 생성형 AI API(NLP)로 비정형 의료보고서를 구조화
-   **오류 검증:** 원본과 정형화 데이터를 비교 및 오류 수정 기능 제공
-   **영상 연계:** 가명화된 연구용 PACS(Orthanc, dcm4chee 등) 연동
-   **인공지능 활용:** 영상 segmentation, AI 학습 자동화

## 주요 기능

-   병리 및 영상판독보고서 가명화 (병록번호의 자리수를 유지하는 format preserving encription)
-   가명화된 비정형 보고서의 NLP 기반 정형화
-   원본-정형화 데이터 비교 및 오류 교정
-   영상파일(PACS) 연동 및 DICOM 데이터 관리
-   오픈소스 기반 영상 segmentation, AI 모델 학습
-   HashiCorp Vault 기반 가명화 키 저장 및 감사로그 구현
-   PostgreSQL 기반 메타데이터 저장/관리

## 개발환경

-   **운영체제:** Windows 10/11, WSL2 Ubuntu
-   **개발언어:** R (\>=4.5.0), Python (=3.12.11) python-fpe 패키지 호환 고려
-   **IDE:** RStudio(rserver), VS Code
-   **DB:** PostgreSQL
-   **버전관리:** git & GitHub
-   **패키지관리:** renv(R), venv(Python)
-   **오픈소스 PACS:** Orthanc, dcm4chee, dcmtk
-   **영상 편집:** 3D Slicer
